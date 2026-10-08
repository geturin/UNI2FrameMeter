"""Read immutable, native-tick snapshots produced by the injected FrameMeter DLL.

The overlay never follows game pointers with ReadProcessMemory. Pointers in a
packet are keys into that packet's bounded chunk directory, not live addresses.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import json
from pathlib import Path
import struct
import subprocess
import sys
from typing import Callable


MAGIC = 0x31464D55
ABI = 1
HEADER_BYTES = 256
SLOT_BYTES = 600 * 1024
CAPACITY = 64
MAX_CHUNKS = 600
DATA_OFFSET = 32 + MAX_CHUNKS * 12
MAPPING_BYTES = HEADER_BYTES + SLOT_BYTES * CAPACITY
FM_VALID = 1
FM_RESET = 2
FM_STARTING = 0
FM_READY = 1
FM_SUSPENDED = 2
FM_FAULT = 3
SUPPORTED_SHA256 = "4ebed985ecbf330ab8e495573361e49df20bb555263289d1aff5425fac9b7ed9"
NATIVE_HOST_NAME = "uni2-frame-meter-host.exe"
NATIVE_DLL_NAME = "uni2-frame-meter.dll"
FILE_MAP_WRITE = 0x0002
FILE_MAP_READ = 0x0004
DWORD_MASK = 0xFFFFFFFF


def runtime_directory() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class HookLayout:
    entity_pool_offset: int
    entity_stride: int
    entity_count: int
    battle_tick_offset: int
    scene_offset: int
    object_count_offset: int
    object_pointers_offset: int
    hook_offset: int


@dataclass(frozen=True)
class SnapshotChunk:
    address: int
    size: int
    offset: int


@dataclass(frozen=True)
class NativeSnapshot:
    sequence: int
    tick: int
    scene: int
    flags: int
    chunks: tuple[SnapshotChunk, ...]
    data: bytes
    dropped_before: int = 0

    def read(self, address: int, size: int) -> bytes | None:
        if size < 0 or address < 0 or address + size > 0x100000000:
            return None
        if size == 0:
            return b""
        for chunk in self.chunks:
            relative = address - chunk.address
            if relative >= 0 and relative + size <= chunk.size:
                return self.data[chunk.offset + relative:chunk.offset + relative + size]
        return None


def decode_snapshot(header: bytes, directory: bytes, data: bytes, expected_sequence: int, dropped_before: int = 0) -> NativeSnapshot:
    if len(header) != 32:
        raise RuntimeError("Native snapshot header is truncated")
    stamp, sequence, tick, scene, chunk_count, used_bytes, flags, _reserved = struct.unpack("<8I", header)
    if stamp & 1 or sequence != expected_sequence or flags & ~(FM_VALID | FM_RESET):
        raise RuntimeError("Native snapshot sequence or flags are invalid")
    if chunk_count > MAX_CHUNKS or used_bytes > SLOT_BYTES - DATA_OFFSET:
        raise RuntimeError("Native snapshot exceeds the shared-memory bounds")
    if len(directory) != chunk_count * 12 or len(data) != used_bytes:
        raise RuntimeError("Native snapshot payload is truncated")
    chunks = tuple(SnapshotChunk(*values) for values in struct.iter_unpack("<III", directory))
    for chunk in chunks:
        if not chunk.address or not chunk.size or chunk.address + chunk.size > 0x100000000 or chunk.offset + chunk.size > used_bytes:
            raise RuntimeError("Native snapshot contains an invalid chunk")
    return NativeSnapshot(sequence, tick, scene, flags, chunks, data, dropped_before)


class RingReader:
    """Bounded seqlock reader; suitable for the real mapping and owned fixtures."""
    def __init__(self, read_bytes: Callable[[int, int], bytes]):
        self.read_bytes = read_bytes
        self.last_sequence = 0
        self.dropped_frames = 0
        self.pending_drops = 0

    def read_available(self, newest_sequence: int) -> list[NativeSnapshot]:
        available = (newest_sequence - self.last_sequence) & DWORD_MASK
        if available == 0:
            return []
        if available > 0x7FFFFFFF:
            raise RuntimeError("Native snapshot sequence moved backwards; restart the game and FrameMeter")
        missing = max(0, available - CAPACITY)
        if missing:
            self.last_sequence = (self.last_sequence + missing) & DWORD_MASK
            self.dropped_frames += missing
            self.pending_drops += missing
        result: list[NativeSnapshot] = []
        for _ in range(min(available, CAPACITY)):
            expected = (self.last_sequence + 1) & DWORD_MASK
            slot = HEADER_BYTES + ((expected - 1) % CAPACITY) * SLOT_BYTES
            packet = None
            for _attempt in range(3):
                stamp_before = self.read_bytes(slot, 4)
                if len(stamp_before) != 4 or struct.unpack("<I", stamp_before)[0] & 1:
                    continue
                header = self.read_bytes(slot, 32)
                if len(header) != 32:
                    raise RuntimeError("Native shared-memory slot is truncated")
                fields = struct.unpack("<8I", header)
                if fields[1] != expected:
                    # The producer may have lapped this reader while copying.
                    # Retain the cursor and let the next header observation
                    # account for the missing records; never count torn data.
                    return result
                chunk_count, used_bytes = fields[4:6]
                if chunk_count > MAX_CHUNKS or used_bytes > SLOT_BYTES - DATA_OFFSET:
                    raise RuntimeError("Native shared-memory packet has invalid bounds")
                directory = self.read_bytes(slot + 32, chunk_count * 12)
                data = self.read_bytes(slot + DATA_OFFSET, used_bytes)
                stamp_after = self.read_bytes(slot, 4)
                if stamp_before != stamp_after or stamp_before != header[:4] or struct.unpack("<I", stamp_after)[0] & 1:
                    continue
                packet = decode_snapshot(header, directory, data, expected, self.pending_drops)
                break
            if packet is None:
                break
            result.append(packet)
            self.last_sequence = expected
            self.pending_drops = 0
        return result


class HookClient:
    def __init__(self, pid: int, image_base: int, digest: str, directory: Path | None = None):
        self.pointer = None
        self.handle = None
        self.mutex = None
        self.closed = False
        self.heartbeat_enabled = False
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel32.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.OpenFileMappingW.restype = wintypes.HANDLE
        self.kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
        self.kernel32.MapViewOfFile.restype = ctypes.c_void_p
        self.kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
        self.kernel32.UnmapViewOfFile.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.GetTickCount.argtypes = []
        self.kernel32.GetTickCount.restype = wintypes.DWORD
        self.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.CreateMutexW.restype = wintypes.HANDLE
        try:
            self._initialize(pid, image_base, digest, directory)
        except BaseException:
            self.close()
            raise

    def _initialize(self, pid: int, image_base: int, digest: str, directory: Path | None = None):
        if digest.lower() != SUPPORTED_SHA256:
            raise RuntimeError("This game update is not supported by this FrameMeter build. No hook was installed. Download a compatible FrameMeter version.\nEXE SHA256: " + digest)
        directory = directory or runtime_directory()
        helper = directory / NATIVE_HOST_NAME
        dll = directory / NATIVE_DLL_NAME
        if not helper.is_file() or not dll.is_file():
            raise RuntimeError("The FrameMeter native helper or DLL is missing. Extract the complete ZIP before launching the overlay.")
        ctypes.set_last_error(0)
        self.mutex = self.kernel32.CreateMutexW(None, False, f"Local\\UNI2FrameMeter-client-v1-{pid}")
        mutex_error = ctypes.get_last_error()
        if not self.mutex:
            raise ctypes.WinError(mutex_error, "Cannot create the FrameMeter client lock")
        if mutex_error == 183:
            raise RuntimeError("UNI2 Frame Meter is already connected to this game. Close the existing FrameMeter window before starting another one.")
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            result = subprocess.run([str(helper), "--attach", str(pid)], cwd=str(directory), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=75, creationflags=creation_flags)
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("FrameMeter native initialization timed out and may still be finishing in the game process. Restart the game before trying FrameMeter again.") from error
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Native hook attachment failed (exit {result.returncode})")
        try:
            reply = json.loads(result.stdout)
        except (ValueError, TypeError) as error:
            raise RuntimeError("Native hook helper returned an invalid attachment result") from error
        expected_name = f"Local\\UNI2FrameMeter-v1-{pid}"
        if reply.get("pid") != pid or reply.get("mapping") != expected_name or reply.get("image_base") != image_base:
            raise RuntimeError("Native hook attachment identity does not match the selected game process")
        self.pid = pid
        self.image_base = image_base
        self.handle = self.kernel32.OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, False, expected_name)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error(), "Cannot open the FrameMeter shared-memory mapping")
        try:
            self.pointer = self.kernel32.MapViewOfFile(self.handle, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, MAPPING_BYTES)
            if not self.pointer:
                raise ctypes.WinError(ctypes.get_last_error(), "Cannot map the FrameMeter native snapshots")
            header = self.read_bytes(0, HEADER_BYTES)
            fields = struct.unpack_from("<20I", header)
            if fields[:6] != (MAGIC, ABI, HEADER_BYTES, SLOT_BYTES, CAPACITY, pid):
                raise RuntimeError("FrameMeter DLL and overlay use incompatible shared-memory formats")
            self.layout = HookLayout(fields[10], fields[11], fields[12], fields[13], fields[14], fields[15], fields[16], fields[17])
            if self.layout.entity_stride != 0xBC0 or self.layout.entity_count != 12:
                raise RuntimeError("FrameMeter DLL reports an unsupported entity layout")
            self.heartbeat_enabled = True
            self.invalid_packets = fields[19]
            self.ring = RingReader(self.read_bytes)
            # Existing resident hooks may have old packets from a closed UI.
            # Start at the current producer cursor and wait for fresh data.
            self.ring.last_sequence = fields[7]
            self.heartbeat()
        except BaseException:
            self.close()
            raise

    def read_bytes(self, offset: int, size: int) -> bytes:
        if self.closed or self.pointer is None:
            raise RuntimeError("FrameMeter shared-memory mapping is closed")
        if offset < 0 or size < 0 or offset + size > MAPPING_BYTES:
            raise RuntimeError("FrameMeter shared-memory read is outside its bounds")
        return ctypes.string_at(self.pointer + offset, size)

    def heartbeat(self) -> None:
        if not self.closed and self.pointer and self.heartbeat_enabled:
            ctypes.c_uint32.from_address(self.pointer + 32).value = self.kernel32.GetTickCount() or 1

    def read_available(self) -> list[NativeSnapshot]:
        self.heartbeat()
        header = self.read_bytes(0, HEADER_BYTES)
        status, newest = struct.unpack_from("<2I", header, 24)
        self.status = status
        self.capture_errors = struct.unpack_from("<I", header, 36)[0]
        self.invalid_packets = struct.unpack_from("<I", header, 76)[0]
        if status == FM_FAULT:
            message = header[80:256].split(b"\0", 1)[0].decode("utf-8", errors="replace")
            raise RuntimeError(message or "The native FrameMeter snapshot hook failed safely")
        if status not in (FM_STARTING, FM_READY, FM_SUSPENDED):
            raise RuntimeError("FrameMeter DLL returned an unknown runtime status")
        return self.ring.read_available(newest)

    @property
    def dropped_frames(self) -> int:
        return self.ring.dropped_frames

    def close(self) -> None:
        if self.closed:
            return
        if self.pointer:
            if self.heartbeat_enabled:
                ctypes.c_uint32.from_address(self.pointer + 32).value = 0
            self.kernel32.UnmapViewOfFile(self.pointer)
            self.pointer = None
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None
        if self.mutex:
            self.kernel32.CloseHandle(self.mutex)
            self.mutex = None
        self.closed = True
