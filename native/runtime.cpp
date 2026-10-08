#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <cstring>
#include "protocol.h"
#include "profile.h"
#include "MinHook.h"

namespace {
using Advance = int (__thiscall *)(const uint8_t*);
Advance original_advance=nullptr;
uintptr_t image=0;
HANDLE mapping=nullptr;
FmShared* shared=nullptr;
volatile LONG started=0, capture_lock=0, armed=0, failed=0, pending_reset=0;
volatile LONG visible_scene=0, visible_frame=0;
uint32_t sequence=0, published_scene=0, published_tick=0;
bool has_frame=false;

void message(const char* text,FmStatus status) {
    if (!shared) return;
    size_t n=std::strlen(text);
    if (n>=sizeof(shared->header.message)) n=sizeof(shared->header.message)-1;
    std::memcpy(shared->header.message,text,n); shared->header.message[n]=0;
    MemoryBarrier(); InterlockedExchange(&shared->header.status,status);
}
void fault(const char* text) {
    InterlockedExchange(&failed,1);
    InterlockedIncrement(&shared->header.capture_errors);
    InterlockedIncrement(&shared->header.invalid_packets);
    message(text,FM_FAULT);
}
bool client_active() {
    const DWORD heartbeat=static_cast<DWORD>(InterlockedCompareExchange(&shared->header.client_heartbeat,0,0));
    return heartbeat && static_cast<DWORD>(GetTickCount()-heartbeat)<=5000;
}
bool training_active() {
    uint32_t mode=0,submode=0; uint8_t network=1;
    return FmGet(image+FM_TRAINING_MODE_RVA,mode) && FmGet(image+FM_TRAINING_SUBMODE_RVA,submode) &&
        FmGet(image+FM_NETWORK_ACTIVE_RVA,network) && !network && ((mode==0 && submode==1) || mode==3);
}
FmSlot& begin_slot(uint32_t tick,uint32_t scene,uint32_t flags) {
    const uint32_t next=sequence+1;
    auto& slot=shared->slots[(next-1)%FM_RING_CAPACITY];
    const uint32_t stamp=static_cast<uint32_t>(InterlockedCompareExchange(&slot.stamp,0,0));
    // A single writer owns capture_lock. Changing an even stamp to odd makes
    // a GUI reject an in-flight copy without waiting for the game thread.
    InterlockedExchange(&slot.stamp,static_cast<LONG>((stamp+1u)|1u));
    slot.sequence=next; slot.tick=tick; slot.scene=scene;
    slot.chunk_count=0; slot.used_bytes=0; slot.flags=flags; slot.reserved=0;
    return slot;
}
void publish(FmSlot& slot) {
    MemoryBarrier();
    const uint32_t stamp=static_cast<uint32_t>(InterlockedCompareExchange(&slot.stamp,0,0));
    InterlockedExchange(&slot.stamp,static_cast<LONG>(stamp+1u));
    sequence=slot.sequence;
    InterlockedExchange(&shared->header.write_seq,static_cast<LONG>(sequence));
}
const uint8_t* add_chunk(FmSlot& slot,uintptr_t address,uint32_t bytes,bool essential) {
    if (!bytes) return nullptr;
    for (uint32_t i=0;i<slot.chunk_count;++i) {
        const auto& chunk=slot.chunks[i];
        if (address>=chunk.address && address-chunk.address<=chunk.size &&
            bytes<=chunk.size-static_cast<uint32_t>(address-chunk.address))
            return slot.data+chunk.offset+(address-chunk.address);
    }
    if (!address || bytes>UINT32_MAX-address || slot.chunk_count>=FM_MAX_CHUNKS ||
        bytes>sizeof(slot.data)-slot.used_bytes) {
        if (essential) fault("Native snapshot exceeded its bounded address/chunk capacity.");
        else InterlockedIncrement(&shared->header.capture_errors);
        return nullptr;
    }
    auto* data=slot.data+slot.used_bytes;
    if (!FmRead(GetCurrentProcess(),address,data,bytes)) {
        if (essential) fault("Required native frame data became unreadable; capture stopped.");
        else InterlockedIncrement(&shared->header.capture_errors);
        return nullptr;
    }
    slot.chunks[slot.chunk_count++]={static_cast<uint32_t>(address),bytes,slot.used_bytes};
    slot.used_bytes+=bytes;
    return data;
}
uint32_t u32(const uint8_t* data,uint32_t offset=0) {
    uint32_t value=0; std::memcpy(&value,data+offset,sizeof(value)); return value;
}
void capture_entity_animation(FmSlot& slot,const uint8_t* entity) {
    if (!entity[FM_ACTIVE_OFFSET]) return;
    const uint32_t animation=u32(entity,FM_ANIMATION_OFFSET);
    if (!animation) return;
    const auto* pointers=add_chunk(slot,static_cast<uintptr_t>(animation)+0x10c,8,true);
    if (!pointers) return;
    const uint32_t descriptor=u32(pointers);
    if (descriptor) add_chunk(slot,static_cast<uintptr_t>(descriptor)+0x0d,0x0f,true);
}
void reset(uint32_t tick,uint32_t scene) {
    if (!has_frame) return;
    auto& slot=begin_slot(tick,scene,FM_RESET);
    publish(slot); has_frame=false; published_scene=scene; published_tick=tick;
    InterlockedExchange(&visible_frame,0);
}
void capture(uint32_t tick,uint32_t scene) {
    auto& slot=begin_slot(tick,scene,FM_VALID);
    // Capture occurs after the original frame routine on its simulation
    // thread. Every dependent byte is copied into the packet before publish.
    if (!add_chunk(slot,image+FM_TICK_RVA,4,true) ||
        !add_chunk(slot,image+FM_PHASE_STATE_RVA,12,true) ||
        !add_chunk(slot,image+FM_SLOW_SKIP_RVA,4,true) ||
        !add_chunk(slot,image+FM_GLOBAL_STOP_RVA,4,true)) return;
    const auto* pool=add_chunk(slot,image+FM_POOL_RVA,FM_ENTITY_STRIDE*FM_ENTITY_COUNT,true);
    const auto* count_raw=add_chunk(slot,image+FM_OBJECT_COUNT_RVA,4,true);
    if (!pool || !count_raw) return;
    const uint32_t count=u32(count_raw);
    if (count>FM_MAX_OBJECTS) { fault("Native object count exceeded the audited 2000-object bound."); return; }
    const auto* pointers=count?add_chunk(slot,image+FM_OBJECT_POINTERS_RVA,count*4,true):nullptr;
    if (count && !pointers) return;
    for (uint32_t i=0;i<FM_ENTITY_COUNT;++i) {
        capture_entity_animation(slot,pool+i*FM_ENTITY_STRIDE);
        if (InterlockedCompareExchange(&failed,0,0)) return;
    }
    const uint32_t summary_bytes=count*sizeof(FmObjectSummary);
    if (summary_bytes) {
        // Full native objects need almost 4 MiB at the real 2000-object limit.
        // Copy only their audited fields into a transport-only summary; no
        // summary address is handed to a general-purpose memory reader.
        if (slot.chunk_count>=FM_MAX_CHUNKS || summary_bytes>sizeof(slot.data)-slot.used_bytes) {
            fault("Object summary exceeded its bounded packet capacity."); return;
        }
        auto* rows=slot.data+slot.used_bytes;
        // data is byte-packed after variable-sized descriptor chunks. Avoid
        // unaligned struct writes by copying each local row with memcpy.
        for (uint32_t i=0;i<count;++i) {
            const uint32_t pointer=u32(pointers,i*4);
            FmObjectSummary row{}; row.index=i; row.address=pointer;
            if (pointer) {
                uint8_t object[FM_OBJECT_BYTES];
                if (!FmRead(GetCurrentProcess(),pointer,object,sizeof(object))) {
                    fault("Required native object data became unreadable; capture stopped."); return;
                }
                row.owner=object[4]; row.object_type=u32(object,0xc);
                row.exist_flags=u32(object,0x84); row.parent_pointer=u32(object,0x3f4);
                row.descriptor_pointer=u32(object,0x650); row.animation_pointer=u32(object,FM_ANIMATION_OFFSET);
                row.cached_attack_pointer=u32(object,0x658); row.move_code=u32(object,0x6b8);
                row.active_marker=object[FM_ACTIVE_OFFSET]; row.frame_attack_pointer=FM_UNKNOWN_POINTER;
                if (row.active_marker && row.animation_pointer &&
                    !FmGet(static_cast<uintptr_t>(row.animation_pointer)+0x110,row.frame_attack_pointer)) {
                    fault("Required native projectile animation data became unreadable; capture stopped."); return;
                }
            }
            std::memcpy(rows+i*sizeof(row),&row,sizeof(row));
        }
        slot.chunks[slot.chunk_count++]={FM_OBJECT_SUMMARY_KEY,summary_bytes,slot.used_bytes};
        slot.used_bytes+=summary_bytes;
    }
    uint32_t after_tick=0;
    if (!FmGet(image+FM_TICK_RVA,after_tick) || after_tick!=tick) {
        InterlockedIncrement(&shared->header.capture_errors);
        InterlockedIncrement(&shared->header.invalid_packets);
        return;
    }
    publish(slot); has_frame=true; published_tick=tick; published_scene=scene;
    InterlockedExchange(&visible_scene,static_cast<LONG>(scene));
    InterlockedExchange(&visible_frame,1);
}
int __fastcall hook_advance(const uint8_t* flags,void*) {
    // Reads preceding the game call must not change its incoming last error.
    const DWORD entry_error=GetLastError();
    uint8_t logic=0; uint32_t before_tick=0;
    const bool before_ok=FmGet(reinterpret_cast<uintptr_t>(flags),logic) && FmGet(image+FM_TICK_RVA,before_tick);
    SetLastError(entry_error);
    const int result=original_advance(flags);
    const DWORD exit_error=GetLastError();
    if (InterlockedCompareExchange(&armed,0,0) && shared) {
        InterlockedIncrement(&shared->header.capture_calls);
        if (InterlockedCompareExchange(&capture_lock,1,0)==0) {
            if (!InterlockedCompareExchange(&failed,0,0) && client_active()) {
                uint32_t tick=0,scene=0;
                const bool current_ok=FmGet(image+FM_TICK_RVA,tick) && FmGet(image+FM_SCENE_RVA,scene);
                if (!before_ok || !current_ok) fault("Required native frame flags, tick or scene became unreadable; capture stopped.");
                else if (InterlockedExchange(&pending_reset,0)) reset(tick,scene);
                if (!InterlockedCompareExchange(&failed,0,0) && training_active() && before_ok && logic && tick!=before_tick) {
                    if (has_frame && (scene!=published_scene || tick<published_tick)) reset(tick,scene);
                    capture(tick,scene);
                }
            }
            InterlockedExchange(&capture_lock,0);
        } else if (before_ok && logic && client_active()) {
            InterlockedIncrement(&shared->header.capture_errors);
            InterlockedIncrement(&shared->header.invalid_packets);
        }
    }
    SetLastError(exit_error);
    return result;
}
DWORD WINAPI control(void*) {
    for (;;) {
        Sleep(100);
        if (!InterlockedCompareExchange(&failed,0,0)) {
            const bool client=client_active();
            const bool training=training_active();
            const LONG desired=client&&training?FM_READY:FM_SUSPENDED;
            LONG previous=InterlockedCompareExchange(&shared->header.status,0,0);
            while (previous!=FM_FAULT && previous!=desired) {
                const LONG actual=InterlockedCompareExchange(&shared->header.status,desired,previous);
                if (actual==previous) break;
                previous=actual;
            }
            uint32_t scene=0;
            if (InterlockedCompareExchange(&visible_frame,0,0) && FmGet(image+FM_SCENE_RVA,scene) &&
                (!client || !training || scene!=static_cast<uint32_t>(InterlockedCompareExchange(&visible_scene,0,0))))
                InterlockedExchange(&pending_reset,1);
        }
    }
}
bool verify_game(uintptr_t candidate) {
    if (!FmGameImage(GetCurrentProcess(),candidate)) return false;
    wchar_t path[32768]; DWORD length=GetModuleFileNameW(nullptr,path,32768);
    if (!length || length>=32768) return false;
    const wchar_t* name=path;
    for (DWORD i=0;i<length;++i) if (path[i]==L'\\' || path[i]==L'/') name=path+i+1;
    if (_wcsicmp(name,L"uni2.exe")) return false;
    HANDLE file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if (file==INVALID_HANDLE_VALUE) return false;
    LARGE_INTEGER size{}; std::string hash;
    const bool ok=GetFileSizeEx(file,&size) && size.QuadPart==FM_IMAGE_BYTES && FmSha256(file,hash) && hash==FM_GAME_SHA256;
    CloseHandle(file); return ok;
}
}

// Export is called by the helper outside the Windows loader lock. Error codes
// distinguish image/signature rejection from mapping and hook failures.
extern "C" __declspec(dllexport) DWORD WINAPI FrameMeterStart(void*) {
    static_assert(sizeof(void*)==4,"The injected game module must be PE32");
    const uintptr_t candidate=reinterpret_cast<uintptr_t>(GetModuleHandleW(nullptr));
    if (!verify_game(candidate)) return 2;
    if (InterlockedCompareExchange(&started,1,0)) {
        if (InterlockedCompareExchange(&armed,0,0) && shared) return shared->header.status==FM_FAULT?13:0;
        return 14;
    }
    image=candidate;
    if (!FmHookSignature(GetCurrentProcess(),image)) { InterlockedExchange(&started,0); return 11; }
    HMODULE retained=nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
                           reinterpret_cast<LPCWSTR>(&FrameMeterStart),&retained)) return 13;
    wchar_t name[128]; wsprintfW(name,L"%s%lu",FM_MAPPING_PREFIX,GetCurrentProcessId());
    mapping=CreateFileMappingW(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,sizeof(FmShared),name);
    const DWORD map_error=GetLastError();
    if (!mapping || map_error==ERROR_ALREADY_EXISTS) { if (mapping) CloseHandle(mapping); mapping=nullptr; return 12; }
    shared=static_cast<FmShared*>(MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,sizeof(FmShared)));
    if (!shared) return 12;
    auto& header=shared->header;
    header.magic=FM_MAGIC; header.abi=FM_ABI; header.header_bytes=FM_HEADER_BYTES;
    header.slot_bytes=FM_SLOT_BYTES; header.capacity=FM_RING_CAPACITY; header.pid=GetCurrentProcessId();
    header.pool_rva=FM_POOL_RVA; header.entity_stride=FM_ENTITY_STRIDE; header.entity_count=FM_ENTITY_COUNT;
    header.tick_rva=FM_TICK_RVA; header.scene_rva=FM_SCENE_RVA;
    header.object_count_rva=FM_OBJECT_COUNT_RVA; header.object_pointers_rva=FM_OBJECT_POINTERS_RVA; header.hook_rva=FM_HOOK_RVA;
    message("Installing the native frame-completion observer.",FM_STARTING);
    if (MH_Initialize()!=MH_OK || MH_CreateHook(reinterpret_cast<void*>(image+FM_HOOK_RVA),
        reinterpret_cast<void*>(&hook_advance),reinterpret_cast<void**>(&original_advance))!=MH_OK) {
        message("Could not create native frame hook. Collection remains disabled.",FM_FAULT); return 13;
    }
    HANDLE thread=CreateThread(nullptr,0,&control,nullptr,CREATE_SUSPENDED,nullptr);
    if (!thread) { MH_RemoveHook(reinterpret_cast<void*>(image+FM_HOOK_RVA)); message("Could not create capture control thread.",FM_FAULT); return 13; }
    if (MH_EnableHook(reinterpret_cast<void*>(image+FM_HOOK_RVA))!=MH_OK) {
        // No target code is called or replaced when enable fails.
        MH_RemoveHook(reinterpret_cast<void*>(image+FM_HOOK_RVA));
        // Resume the owned control thread; it remains inert in FM_FAULT.
        message("Could not enable frame hook. Restart the game before retrying.",FM_FAULT);
        ResumeThread(thread); CloseHandle(thread); return 13;
    }
    // Publish READY before arming capture. Once armed, a game-thread fault
    // must never be overwritten by the initialization thread.
    message("Native frame hook ready. Waiting for the overlay heartbeat.",FM_READY);
    InterlockedExchange(&armed,1);
    ResumeThread(thread); CloseHandle(thread); return 0;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID) {
    if (reason==DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(module);
    return TRUE;
}
