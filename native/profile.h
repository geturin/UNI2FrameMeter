#pragma once
#include <windows.h>
#include <wincrypt.h>
#include <stdint.h>
#include <cstring>
#include <limits>
#include <string>

// This profile identifies the inspected image. Future updates require a new
// producer/layout audit; matching a filename or an old absolute VA is unsafe.
constexpr char FM_GAME_SHA256[] = "4ebed985ecbf330ab8e495573361e49df20bb555263289d1aff5425fac9b7ed9";
constexpr uint32_t FM_IMAGE_BYTES = 6921216;
constexpr uint32_t FM_IMAGE_SIZE = 0x44e5000;
constexpr uint32_t FM_IMAGE_TIMESTAMP = 0x6abcb77f;
constexpr uint32_t FM_HOOK_RVA = 0x126660;
constexpr uint32_t FM_POOL_RVA = 0xc65280;
constexpr uint32_t FM_ENTITY_STRIDE = 0xbc0;
constexpr uint32_t FM_ENTITY_COUNT = 12;
// The elapsed scene-frame counter advances once in every unpaused logic pass,
// including slowdown/global-freeze repeats. The phase counter may stay still.
constexpr uint32_t FM_TICK_RVA = 0x5a58c4;
constexpr uint32_t FM_PHASE_STATE_RVA = 0x5a4b2c;
constexpr uint32_t FM_PHASE_TICK_RVA = 0x5a4b34;
constexpr uint32_t FM_SLOW_SKIP_RVA = 0x657e78;
constexpr uint32_t FM_GLOBAL_STOP_RVA = 0x657e80;
constexpr uint32_t FM_SCENE_RVA = 0x5a4a84;
constexpr uint32_t FM_OBJECT_COUNT_RVA = 0x87b4e0;
constexpr uint32_t FM_OBJECT_POINTERS_RVA = 0x87b4e4;
constexpr uint32_t FM_MAX_OBJECTS = 2000;
constexpr uint32_t FM_OBJECT_BYTES = 0x7dc;
constexpr uint32_t FM_ANIMATION_OFFSET = 0x654;
constexpr uint32_t FM_ACTIVE_OFFSET = 0x7d8;
constexpr uint32_t FM_TRAINING_MODE_RVA = 0x5a5948;
constexpr uint32_t FM_TRAINING_SUBMODE_RVA = 0x5a594c;
constexpr uint32_t FM_NETWORK_ACTIVE_RVA = 0x1d595ed;
constexpr uint8_t FM_HOOK_BYTES[] = {
    0x53,0x8b,0xdc,0x83,0xec,0x08,0x83,0xe4,0xf8,0x83,0xc4,
    0x04,0x55,0x8b,0x6b,0x04,0x89,0x6c,0x24,0x04,0x8b,0xec
};

inline bool FmRead(HANDLE process, uintptr_t address, void* out, size_t bytes) {
    if (!address || bytes > std::numeric_limits<uintptr_t>::max()-address) return false;
    SIZE_T done=0;
    return ReadProcessMemory(process,reinterpret_cast<const void*>(address),out,bytes,&done) && done==bytes;
}
template<class T> inline bool FmGet(uintptr_t address,T& out) {
    return FmRead(GetCurrentProcess(),address,&out,sizeof(out));
}
inline bool FmGameImage(HANDLE process,uintptr_t base) {
    IMAGE_DOS_HEADER dos{}; IMAGE_NT_HEADERS32 nt{};
    if (!FmRead(process,base,&dos,sizeof(dos)) || dos.e_magic!=IMAGE_DOS_SIGNATURE ||
        dos.e_lfanew<static_cast<LONG>(sizeof(dos)) || dos.e_lfanew>1024*1024 ||
        !FmRead(process,base+static_cast<uint32_t>(dos.e_lfanew),&nt,sizeof(nt))) return false;
    return nt.Signature==IMAGE_NT_SIGNATURE && nt.FileHeader.Machine==IMAGE_FILE_MACHINE_I386 &&
        nt.FileHeader.SizeOfOptionalHeader==sizeof(IMAGE_OPTIONAL_HEADER32) &&
        nt.OptionalHeader.Magic==IMAGE_NT_OPTIONAL_HDR32_MAGIC &&
        nt.OptionalHeader.SizeOfImage==FM_IMAGE_SIZE && nt.FileHeader.TimeDateStamp==FM_IMAGE_TIMESTAMP;
}
inline bool FmHookSignature(HANDLE process,uintptr_t base) {
    uint8_t bytes[sizeof(FM_HOOK_BYTES)]{};
    return FmRead(process,base+FM_HOOK_RVA,bytes,sizeof(bytes)) && !std::memcmp(bytes,FM_HOOK_BYTES,sizeof(bytes));
}
inline bool FmSha256(HANDLE file,std::string& text) {
    HCRYPTPROV provider=0; HCRYPTHASH hash=0;
    if (!CryptAcquireContextW(&provider,nullptr,nullptr,PROV_RSA_AES,CRYPT_VERIFYCONTEXT)) return false;
    if (!CryptCreateHash(provider,CALG_SHA_256,0,0,&hash)) { CryptReleaseContext(provider,0); return false; }
    LARGE_INTEGER zero{}; bool ok=SetFilePointerEx(file,zero,nullptr,FILE_BEGIN)!=FALSE;
    uint8_t buffer[65536];
    while (ok) {
        DWORD bytes=0;
        if (!ReadFile(file,buffer,sizeof(buffer),&bytes,nullptr)) { ok=false; break; }
        if (!bytes) break;
        if (!CryptHashData(hash,buffer,bytes,0)) { ok=false; break; }
    }
    uint8_t digest[32]{}; DWORD bytes=sizeof(digest);
    if (ok) ok=CryptGetHashParam(hash,HP_HASHVAL,digest,&bytes,0)!=FALSE && bytes==sizeof(digest);
    CryptDestroyHash(hash); CryptReleaseContext(provider,0);
    if (!ok) return false;
    constexpr char hex[]="0123456789abcdef";
    text.clear(); text.reserve(64);
    for (uint8_t byte:digest) { text.push_back(hex[byte>>4]); text.push_back(hex[byte&15]); }
    return true;
}
