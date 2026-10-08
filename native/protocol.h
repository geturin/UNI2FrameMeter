#pragma once
#include <windows.h>
#include <stdint.h>
#include <stddef.h>

constexpr uint32_t FM_MAGIC = 0x31464d55; // UMF1
constexpr uint32_t FM_ABI = 1;
constexpr uint32_t FM_HEADER_BYTES = 256;
constexpr uint32_t FM_SLOT_BYTES = 600 * 1024;
constexpr uint32_t FM_RING_CAPACITY = 64;
constexpr uint32_t FM_MAX_CHUNKS = 600;
constexpr wchar_t FM_MAPPING_PREFIX[] = L"Local\\UNI2FrameMeter-v1-";
// Transport-only chunk key. It never represents readable game memory.
constexpr uint32_t FM_OBJECT_SUMMARY_KEY = 0xff000000;
constexpr uint32_t FM_UNKNOWN_POINTER = 0xffffffff;
struct FmObjectSummary {
    uint32_t index, address, owner, object_type, exist_flags, parent_pointer;
    uint32_t descriptor_pointer, animation_pointer, frame_attack_pointer;
    uint32_t cached_attack_pointer, move_code, active_marker;
};
static_assert(sizeof(FmObjectSummary)==48,"object summary wire row");

enum FmStatus : uint32_t { FM_STARTING=0, FM_READY=1, FM_SUSPENDED=2, FM_FAULT=3 };
enum FmFlags : uint32_t { FM_VALID=1, FM_RESET=2 };

// DWORD-only wire format: usable by both a 64-bit overlay and a 32-bit DLL.
struct FmHeader {
    uint32_t magic, abi, header_bytes, slot_bytes, capacity, pid;
    volatile LONG status, write_seq, client_heartbeat, capture_errors;
    uint32_t pool_rva, entity_stride, entity_count, tick_rva, scene_rva;
    uint32_t object_count_rva, object_pointers_rva, hook_rva;
    volatile LONG capture_calls, invalid_packets;
    char message[176];
};
struct FmChunk { uint32_t address, size, offset; };
struct FmSlot {
    volatile LONG stamp;
    uint32_t sequence, tick, scene, chunk_count, used_bytes, flags, reserved;
    FmChunk chunks[FM_MAX_CHUNKS];
    uint8_t data[FM_SLOT_BYTES - 32 - sizeof(FmChunk)*FM_MAX_CHUNKS];
};
struct FmShared { FmHeader header; FmSlot slots[FM_RING_CAPACITY]; };
static_assert(sizeof(FmHeader)==FM_HEADER_BYTES, "wire header");
static_assert(offsetof(FmSlot,data)==7232 && sizeof(FmSlot)==FM_SLOT_BYTES, "wire slot");
static_assert(sizeof(FmShared)==FM_HEADER_BYTES+FM_SLOT_BYTES*FM_RING_CAPACITY, "wire mapping");
