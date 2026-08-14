from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import time
from dataclasses import dataclass
from typing import Iterable


if sys.platform != "win32":
    raise SystemExit("uni2_probe only supports Windows")


EXPECTED_SHA256 = "55615E8B2A91BE57EDD5EFF68EC0E283D8F0591F1977BB6F0B8A8DDB7AF2EC22"
PROCESS_NAME = "uni2.exe"

# Deliberately read-only process rights.
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
READ_ONLY_PROCESS_RIGHTS = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION

TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

MEM_COMMIT = 0x1000
MEM_IMAGE = 0x1000000
MEM_MAPPED = 0x40000
MEM_PRIVATE = 0x20000

PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100

READABLE_BASE_PROTECTIONS = {
    PAGE_READONLY,
    PAGE_READWRITE,
    PAGE_WRITECOPY,
    PAGE_EXECUTE_READ,
    PAGE_EXECUTE_READWRITE,
    PAGE_EXECUTE_WRITECOPY,
}
WRITABLE_BASE_PROTECTIONS = {
    PAGE_READWRITE,
    PAGE_WRITECOPY,
    PAGE_EXECUTE_READWRITE,
    PAGE_EXECUTE_WRITECOPY,
}

MAX_32BIT_ADDRESS = 0x1_0000_0000
SCAN_CHUNK_SIZE = 1 << 20
WATCH_PAGE_SIZE = 0x10000


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", wintypes.HMODULE),
        ("szModule", wintypes.WCHAR * 256),
        ("szExePath", wintypes.WCHAR * 260),
    ]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL
kernel32.Module32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
kernel32.Module32FirstW.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.VirtualQueryEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
    ctypes.c_size_t,
]
kernel32.VirtualQueryEx.restype = ctypes.c_size_t
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL


def win_error(message: str) -> OSError:
    return ctypes.WinError(ctypes.get_last_error(), message)


@dataclass(frozen=True)
class ModuleInfo:
    base: int
    size: int
    path: str


@dataclass(frozen=True)
class MemoryRegion:
    base: int
    size: int
    protect: int
    kind: int

    @property
    def end(self) -> int:
        return self.base + self.size


@dataclass
class Candidate:
    address: int
    first_value: int
    last_value: int
    observations: int = 1
    increments: int = 0
    stationary: int = 0
    rejected: bool = False
    last_time: float = 0.0


class ProcessHandle:
    def __init__(self, pid: int):
        self.pid = pid
        self.handle = kernel32.OpenProcess(READ_ONLY_PROCESS_RIGHTS, False, pid)
        if not self.handle:
            raise win_error(f"OpenProcess({pid}) failed")

    def close(self) -> None:
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self) -> "ProcessHandle":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def image_path(self) -> str:
        capacity = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(capacity.value)
        if not kernel32.QueryFullProcessImageNameW(
            self.handle, 0, buffer, ctypes.byref(capacity)
        ):
            raise win_error("QueryFullProcessImageNameW failed")
        return buffer.value

    def read(self, address: int, size: int) -> bytes | None:
        if size <= 0:
            return b""
        buffer = ctypes.create_string_buffer(size)
        received = ctypes.c_size_t()
        ok = kernel32.ReadProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(received),
        )
        if not ok or received.value != size:
            return None
        return buffer.raw


def find_process_id(executable_name: str = PROCESS_NAME) -> int | None:
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise win_error("CreateToolhelp32Snapshot(processes) failed")
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
            raise win_error("Process32FirstW failed")
        while True:
            if entry.szExeFile.casefold() == executable_name.casefold():
                return int(entry.th32ProcessID)
            if not kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                break
        return None
    finally:
        kernel32.CloseHandle(snapshot)


def main_module(pid: int) -> ModuleInfo:
    flags = TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32
    snapshot = kernel32.CreateToolhelp32Snapshot(flags, pid)
    if snapshot == INVALID_HANDLE_VALUE:
        raise win_error("CreateToolhelp32Snapshot(modules) failed")
    try:
        entry = MODULEENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        if not kernel32.Module32FirstW(snapshot, ctypes.byref(entry)):
            raise win_error("Module32FirstW failed")
        base = ctypes.cast(entry.modBaseAddr, ctypes.c_void_p).value
        return ModuleInfo(int(base), int(entry.modBaseSize), entry.szExePath)
    finally:
        kernel32.CloseHandle(snapshot)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def protection_base(protect: int) -> int:
    return protect & 0xFF


def is_readable(protect: int) -> bool:
    return not (protect & PAGE_GUARD) and protection_base(protect) in READABLE_BASE_PROTECTIONS


def is_writable(protect: int) -> bool:
    return not (protect & PAGE_GUARD) and protection_base(protect) in WRITABLE_BASE_PROTECTIONS


def enumerate_regions(process: ProcessHandle, writable_only: bool = False) -> list[MemoryRegion]:
    regions: list[MemoryRegion] = []
    address = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while address < MAX_32BIT_ADDRESS:
        result = kernel32.VirtualQueryEx(
            process.handle,
            ctypes.c_void_p(address),
            ctypes.byref(mbi),
            ctypes.sizeof(mbi),
        )
        if not result:
            break
        base = int(mbi.BaseAddress or 0)
        size = int(mbi.RegionSize)
        if size <= 0:
            break
        readable = mbi.State == MEM_COMMIT and is_readable(int(mbi.Protect))
        accepted = readable and (not writable_only or is_writable(int(mbi.Protect)))
        if accepted and base < MAX_32BIT_ADDRESS:
            clipped_size = min(size, MAX_32BIT_ADDRESS - base)
            regions.append(MemoryRegion(base, clipped_size, int(mbi.Protect), int(mbi.Type)))
        next_address = base + size
        if next_address <= address:
            break
        address = next_address
    return regions


def iter_region_blocks(process: ProcessHandle, region: MemoryRegion) -> Iterable[tuple[int, bytes]]:
    offset = 0
    while offset < region.size:
        size = min(SCAN_CHUNK_SIZE, region.size - offset)
        data = process.read(region.base + offset, size)
        if data is not None:
            yield region.base + offset, data
        offset += size


def initial_counter_candidates(
    process: ProcessHandle,
    regions: list[MemoryRegion],
    interval: float,
    min_rate: float,
    max_rate: float,
) -> dict[int, Candidate]:
    first: dict[int, tuple[bytes, float]] = {}
    for region in regions:
        for address, data in iter_region_blocks(process, region):
            first[address] = (data, time.perf_counter())

    time.sleep(interval)

    candidates: dict[int, Candidate] = {}
    for region in regions:
        for address, second in iter_region_blocks(process, region):
            captured = first.get(address)
            if captured is None:
                continue
            original, first_time = captured
            second_time = time.perf_counter()
            if len(original) != len(second):
                continue
            elapsed = max(interval, second_time - first_time)
            minimum = max(1, int(elapsed * min_rate))
            maximum = max(minimum, int(elapsed * max_rate + 2))
            usable = len(second) - (len(second) % 4)
            for offset in range(0, usable, 4):
                old = struct.unpack_from("<I", original, offset)[0]
                new = struct.unpack_from("<I", second, offset)[0]
                delta = (new - old) & 0xFFFFFFFF
                if minimum <= delta <= maximum:
                    absolute = address + offset
                    candidates[absolute] = Candidate(
                        absolute,
                        old,
                        new,
                        observations=2,
                        increments=1,
                        last_time=second_time,
                    )
    return candidates


def read_candidate_pages(process: ProcessHandle, addresses: Iterable[int]) -> dict[int, int]:
    pages: dict[int, list[int]] = {}
    for address in addresses:
        page = address & ~(WATCH_PAGE_SIZE - 1)
        pages.setdefault(page, []).append(address)

    values: dict[int, int] = {}
    for page, page_addresses in pages.items():
        data = process.read(page, WATCH_PAGE_SIZE)
        if data is None:
            for address in page_addresses:
                scalar = process.read(address, 4)
                if scalar is not None:
                    values[address] = struct.unpack("<I", scalar)[0]
            continue
        for address in page_addresses:
            offset = address - page
            if offset + 4 <= len(data):
                values[address] = struct.unpack_from("<I", data, offset)[0]
    return values


def refine_candidates(
    process: ProcessHandle,
    candidates: dict[int, Candidate],
    duration: float,
    interval: float,
    max_rate: float,
) -> None:
    deadline = time.perf_counter() + duration
    while candidates and time.perf_counter() < deadline:
        started = time.perf_counter()
        values = read_candidate_pages(process, candidates.keys())
        observed_at = time.perf_counter()
        for address, candidate in candidates.items():
            value = values.get(address)
            if value is None:
                candidate.rejected = True
                continue
            delta = (value - candidate.last_value) & 0xFFFFFFFF
            elapsed = max(0.001, observed_at - candidate.last_time)
            maximum_delta = max(2, int(max_rate * elapsed + 2))
            candidate.observations += 1
            if delta == 0:
                candidate.stationary += 1
            elif delta <= maximum_delta:
                candidate.increments += 1
            else:
                candidate.rejected = True
            candidate.last_value = value
            candidate.last_time = observed_at
        sleep_for = interval - (time.perf_counter() - started)
        if sleep_for > 0:
            time.sleep(sleep_for)


def candidate_score(candidate: Candidate) -> float:
    if candidate.rejected or candidate.observations <= 1:
        return 0.0
    useful = candidate.increments + candidate.stationary
    return useful / (candidate.observations - 1)


def require_process() -> tuple[int, ProcessHandle, ModuleInfo, str]:
    pid = find_process_id()
    if pid is None:
        raise RuntimeError("uni2.exe is not running")
    process = ProcessHandle(pid)
    try:
        module = main_module(pid)
        image_path = process.image_path()
        digest = sha256_file(image_path)
        return pid, process, module, digest
    except Exception:
        process.close()
        raise


def relative_label(address: int, module: ModuleInfo) -> str | None:
    if module.base <= address < module.base + module.size:
        return f"uni2.exe+0x{address - module.base:X}"
    return None


def command_status(_args: argparse.Namespace) -> int:
    pid = find_process_id()
    if pid is None:
        print("status: NOT_RUNNING")
        return 2
    with ProcessHandle(pid) as process:
        module = main_module(pid)
        path = process.image_path()
        digest = sha256_file(path)
        print(f"status: RUNNING")
        print(f"pid: {pid}")
        print(f"path: {path}")
        print(f"sha256: {digest}")
        print(f"expected_sha256: {EXPECTED_SHA256}")
        print(f"version_match: {str(digest == EXPECTED_SHA256).lower()}")
        print(f"module_base: 0x{module.base:08X}")
        print(f"module_size: 0x{module.size:X}")
        print(f"process_rights: 0x{READ_ONLY_PROCESS_RIGHTS:04X} (QUERY_INFORMATION | VM_READ)")
    return 0


def command_regions(_args: argparse.Namespace) -> int:
    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")
        regions = enumerate_regions(process, writable_only=True)
        total = sum(region.size for region in regions)
        print(f"pid={pid} module=0x{module.base:08X} writable_regions={len(regions)} bytes={total}")
        by_kind: dict[int, int] = {}
        for region in regions:
            by_kind[region.kind] = by_kind.get(region.kind, 0) + region.size
        for kind, size in sorted(by_kind.items()):
            print(f"type=0x{kind:X} bytes={size}")
    return 0


def command_scan_counter(args: argparse.Namespace) -> int:
    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")
        regions = enumerate_regions(process, writable_only=True)
        if args.scope == "module":
            module_end = module.base + module.size
            regions = [
                region
                for region in regions
                if region.base < module_end and region.end > module.base
            ]
        elif args.scope == "private":
            regions = [region for region in regions if region.kind == MEM_PRIVATE]
        total = sum(region.size for region in regions)
        print(f"Reading {len(regions)} writable regions ({total / (1024 * 1024):.1f} MiB).")
        print("Keep the training match actively running during this scan.")
        candidates = initial_counter_candidates(
            process, regions, args.interval, args.min_rate, args.max_rate
        )
        print(f"Initial candidates: {len(candidates)}")
        remaining = max(0.0, args.duration - args.interval)
        refine_candidates(process, candidates, remaining, args.interval, args.max_rate)

        accepted = [
            candidate
            for candidate in candidates.values()
            if candidate_score(candidate) >= 0.999
            and candidate.increments >= max(2, (candidate.observations - 1) // 2)
        ]
        accepted.sort(key=lambda item: (-item.increments, item.address))
        output = {
            "schema": 1,
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": pid,
            "image_sha256": digest,
            "module_base": module.base,
            "module_size": module.size,
            "scan": {
                "duration_seconds": args.duration,
                "interval_seconds": args.interval,
                "min_rate": args.min_rate,
                "max_rate": args.max_rate,
                "scope": args.scope,
            },
            "candidates": [
                {
                    "address": candidate.address,
                    "address_hex": f"0x{candidate.address:08X}",
                    "module_relative": relative_label(candidate.address, module),
                    "first_value": candidate.first_value,
                    "last_value": candidate.last_value,
                    "observations": candidate.observations,
                    "increments": candidate.increments,
                    "stationary": candidate.stationary,
                }
                for candidate in accepted[: args.limit]
            ],
        }
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"Accepted candidates: {len(accepted)} (saved {min(len(accepted), args.limit)})")
        print(f"Output: {destination.resolve()}")
        for item in output["candidates"][:20]:
            label = item["module_relative"] or item["address_hex"]
            print(f"  {label:24} {item['first_value']} -> {item['last_value']}")
    return 0


def command_watch(args: argparse.Namespace) -> int:
    profile = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    pid, process, module, digest = require_process()
    with process:
        if digest != profile["image_sha256"]:
            raise RuntimeError("candidate profile belongs to a different uni2.exe")
        addresses = [int(item["address"]) for item in profile["candidates"]]
        if not addresses:
            raise RuntimeError("candidate profile contains no addresses")
        previous = read_candidate_pages(process, addresses)
        print(f"Watching {len(addresses)} candidates. Press Ctrl+C to stop.")
        started = time.perf_counter()
        try:
            while args.duration <= 0 or time.perf_counter() - started < args.duration:
                time.sleep(args.interval)
                current = read_candidate_pages(process, addresses)
                changes = []
                for address in addresses:
                    old = previous.get(address)
                    new = current.get(address)
                    if old is not None and new is not None and old != new:
                        label = relative_label(address, module) or f"0x{address:08X}"
                        delta = (new - old) & 0xFFFFFFFF
                        changes.append(f"{label} {old}->{new} (+{delta})")
                if changes:
                    stamp = time.perf_counter() - started
                    print(f"[{stamp:8.3f}] " + " | ".join(changes))
                previous = current
        except KeyboardInterrupt:
            pass
    return 0


def command_sample(args: argparse.Namespace) -> int:
    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")
        if args.relative:
            offset = int(args.relative, 0)
            address = module.base + offset
            label = f"uni2.exe+0x{offset:X}"
        else:
            address = int(args.address, 0)
            label = f"0x{address:08X}"
        previous = None
        started = time.perf_counter()
        changes: list[dict[str, float | int]] = []
        reads = 0
        while time.perf_counter() - started < args.duration:
            raw = process.read(address, 4)
            if raw is None:
                raise RuntimeError(f"unable to read {label}")
            value = struct.unpack("<I", raw)[0]
            reads += 1
            if previous is None or value != previous:
                now = time.perf_counter() - started
                delta = None if previous is None else ((value - previous) & 0xFFFFFFFF)
                changes.append({"time": now, "value": value, "delta": delta})
                previous = value
            if args.sleep > 0:
                time.sleep(args.sleep)
        deltas = [int(item["delta"]) for item in changes if item["delta"] is not None]
        elapsed = time.perf_counter() - started
        print(f"address: {label}")
        print(f"duration: {elapsed:.6f}")
        print(f"reads: {reads}")
        print(f"changes: {max(0, len(changes) - 1)}")
        print(f"rate_hz: {max(0, len(changes) - 1) / elapsed:.3f}")
        print(f"unit_deltas: {sum(delta == 1 for delta in deltas)}/{len(deltas)}")
        print(f"max_delta: {max(deltas, default=0)}")
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "pid": pid,
                    "image_sha256": digest,
                    "module_base": module.base,
                    "address": address,
                    "module_relative": relative_label(address, module),
                    "duration": elapsed,
                    "reads": reads,
                    "changes": changes,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"output: {destination.resolve()}")
    return 0


def command_dump(args: argparse.Namespace) -> int:
    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")
        center = module.base + int(args.relative, 0)
        start = center + args.before
        if start < 0 or args.size <= 0:
            raise ValueError("invalid dump range")
        data = process.read(start, args.size)
        if data is None:
            raise RuntimeError("unable to read dump range")
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        print(f"range: 0x{start:08X}-0x{start + len(data):08X}")
        print(f"module_relative: 0x{start - module.base:X}-0x{start + len(data) - module.base:X}")
        print(f"output: {destination.resolve()}")
        for offset in range(0, len(data), 16):
            chunk = data[offset : offset + 16]
            hex_bytes = " ".join(f"{byte:02X}" for byte in chunk)
            ascii_bytes = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in chunk)
            print(f"{start + offset:08X}  {hex_bytes:<47}  {ascii_bytes}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only UNI2 process research probe")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="show target identity and read-only access")
    status.set_defaults(func=command_status)

    regions = subparsers.add_parser("regions", help="summarize readable writable memory")
    regions.set_defaults(func=command_regions)

    scan = subparsers.add_parser("scan-counter", help="find simulation-rate uint32 counters")
    scan.add_argument("--duration", type=float, default=5.0)
    scan.add_argument("--interval", type=float, default=0.25)
    scan.add_argument("--min-rate", type=float, default=30.0)
    scan.add_argument("--max-rate", type=float, default=90.0)
    scan.add_argument("--limit", type=int, default=500)
    scan.add_argument("--scope", choices=("module", "private", "all"), default="module")
    scan.add_argument("--out", default="captures/counter_candidates.json")
    scan.set_defaults(func=command_scan_counter)

    watch = subparsers.add_parser("watch", help="watch previously found candidates")
    watch.add_argument("--candidates", default="captures/counter_candidates.json")
    watch.add_argument("--interval", type=float, default=0.25)
    watch.add_argument("--duration", type=float, default=0.0, help="0 means until Ctrl+C")
    watch.set_defaults(func=command_watch)

    sample = subparsers.add_parser("sample", help="sample one uint32 address at high frequency")
    target = sample.add_mutually_exclusive_group(required=True)
    target.add_argument("--relative", help="module-relative offset, e.g. 0x596B34")
    target.add_argument("--address", help="absolute address")
    sample.add_argument("--duration", type=float, default=2.0)
    sample.add_argument("--sleep", type=float, default=0.001)
    sample.add_argument("--out", default="captures/high_frequency_sample.json")
    sample.set_defaults(func=command_sample)

    dump = subparsers.add_parser("dump", help="read and display a module-relative byte range")
    dump.add_argument("--relative", required=True)
    dump.add_argument("--before", type=lambda value: int(value, 0), default=-0x80)
    dump.add_argument("--size", type=lambda value: int(value, 0), default=0x200)
    dump.add_argument("--out", default="captures/memory_dump.bin")
    dump.set_defaults(func=command_dump)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
