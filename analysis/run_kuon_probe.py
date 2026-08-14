from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import ctypes
from ctypes import wintypes


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "src"))

from list_unib_index import parse_index  # noqa: E402
from uni2_frame_reader import (  # noqa: E402
    BATTLE_TICK_OFFSET,
    ENTITY_COUNT,
    ENTITY_POOL_OFFSET,
    ENTITY_STRIDE,
)
from uni2_probe import (  # noqa: E402
    EXPECTED_SHA256,
    ProcessHandle,
    main_module,
)


GAME_ROOT = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\UNDER NIGHT IN-BIRTH II Sys Celes"
)
GAME_EXE = GAME_ROOT / "uni2.exe"
STEAM_EXE = Path(r"C:\Program Files (x86)\Steam\steam.exe")
STEAM_APP_ID = "2076010"
STEAM_MANIFEST = STEAM_EXE.parent / "steamapps" / f"appmanifest_{STEAM_APP_ID}.acf"
DATA_ROOT = GAME_ROOT / "d"
INDEX_PATH = DATA_ROOT / "hexeojmpimrjs"
LOGICAL_PATH = "data/chr023/chr023_mv_0.txt"
EXPECTED_INDEX_SHA256 = "B65F0CF7ECDA73F1F1D2FD439E88BFF93F40C9CCB9FD9B9CA195F0222DE173DC"
EXPECTED_ENTRY_SHA256 = "220D0B59DBDDADAF4CDE083DE727A0850353020242F4085DBB77E32F0F25C6A2"
WM_CLOSE = 0x0010
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_TERMINATE = 0x0001


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
]
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def game_pids() -> set[int]:
    """Return only processes whose full executable path is the pinned UNI2 binary."""
    output = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq uni2.exe", "/FO", "CSV", "/NH"],
        check=False,
        capture_output=True,
        text=True,
        encoding="mbcs",
    ).stdout
    result: set[int] = set()
    for line in output.splitlines():
        fields = [field.strip('"') for field in line.split('","')]
        if len(fields) < 2 or fields[0].lower() != "uni2.exe":
            continue
        try:
            pid = int(fields[1])
        except ValueError:
            continue
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            continue
        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                if Path(buffer.value).resolve() == GAME_EXE.resolve():
                    result.add(pid)
        finally:
            kernel32.CloseHandle(handle)
    return result


def close_game(timeout: float = 10.0, force: bool = False) -> None:
    pids = game_pids()
    if not pids:
        return

    @WNDENUMPROC
    def callback(hwnd: int, _lparam: int) -> bool:
        window_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value in pids:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True

    user32.EnumWindows(callback, 0)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not (game_pids() & pids):
            return
        time.sleep(0.2)
    remaining = game_pids() & pids
    if force:
        for pid in remaining:
            handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if handle:
                try:
                    kernel32.TerminateProcess(handle, 1)
                finally:
                    kernel32.CloseHandle(handle)
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and (game_pids() & remaining):
            time.sleep(0.1)
        remaining = game_pids() & remaining
    if remaining:
        raise RuntimeError(f"UNI2 processes did not close: {sorted(remaining)}")


def locate_entry() -> tuple[Path, object]:
    archive_name, entries = parse_index(INDEX_PATH)
    entry = next(
        (
            item
            for item in entries
            if item.logical_path.replace("\\", "/").lower() == LOGICAL_PATH.lower()
        ),
        None,
    )
    if entry is None:
        raise RuntimeError(f"index does not contain {LOGICAL_PATH}")
    return INDEX_PATH.parent / archive_name, entry


def read_entry(archive_path: Path, entry: object) -> bytes:
    with archive_path.open("rb") as stream:
        stream.seek(entry.offset)
        data = stream.read(entry.stored_size)
    if len(data) != entry.stored_size:
        raise RuntimeError("short read from archive entry")
    return data


def write_entry(archive_path: Path, entry: object, data: bytes) -> None:
    if len(data) != entry.stored_size:
        raise ValueError("in-place probe entry must preserve its exact stored size")
    with archive_path.open("r+b", buffering=0) as stream:
        stream.seek(entry.offset)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if read_entry(archive_path, entry) != data:
        raise RuntimeError("archive entry verification failed after write")


def wait_for_process(timeout: float = 90.0):
    deadline = time.monotonic() + timeout
    last_error = "process has not appeared"
    while time.monotonic() < deadline:
        for pid in game_pids():
            process = None
            try:
                process = ProcessHandle(pid)
                module = main_module(pid)
                image_path = process.image_path()
                digest = sha256_file(Path(image_path))
                if digest != EXPECTED_SHA256:
                    raise RuntimeError("uni2.exe executable hash is unsupported")
                return pid, process, module, digest
            except (OSError, RuntimeError) as error:
                last_error = f"pid {pid}: {error}"
                if process is not None:
                    process.close()
        time.sleep(0.25)
    raise RuntimeError(f"timed out waiting for UNI2: {last_error}")


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def p1_entity(pool: bytes) -> bytes | None:
    for slot in range(ENTITY_COUNT):
        start = slot * ENTITY_STRIDE
        entity = pool[start : start + ENTITY_STRIDE]
        if u32(entity, 0x7BC) and entity[0x438] == 0 and entity[0x05] == 23:
            return entity
    return None


def state_label(entity: bytes) -> bytes:
    return entity[0xACC:0xB20].split(b"\0", 1)[0]


def capture_cycle(
    process,
    module_base: int,
    destination: Path,
    cycle_frames: int,
    wait_timeout: float = 120.0,
) -> dict[str, object]:
    tick_address = module_base + BATTLE_TICK_OFFSET
    pool_address = module_base + ENTITY_POOL_OFFSET
    pool_size = ENTITY_STRIDE * ENTITY_COUNT
    deadline = time.monotonic() + wait_timeout
    previous_tick: int | None = None
    armed = False
    while time.monotonic() < deadline:
        raw_tick = process.read(tick_address, 4)
        pool = process.read(pool_address, pool_size)
        if raw_tick is None or pool is None:
            time.sleep(0.01)
            continue
        tick = u32(raw_tick, 0)
        if tick == previous_tick:
            time.sleep(0.001)
            continue
        previous_tick = tick
        entity = p1_entity(pool)
        if entity is None or state_label(entity) != b"Mv_Neutral":
            continue
        action_frame = u32(entity, 0x674)
        if action_frame % cycle_frames <= 2:
            armed = True
            break
    if not armed:
        raise RuntimeError("timed out waiting for Kuon neutral probe-cycle boundary")

    destination.parent.mkdir(parents=True, exist_ok=True)
    frames = 0
    first_tick = previous_tick
    first_action_frame = action_frame
    started = time.perf_counter()
    with destination.open("wb") as stream:
        stream.write(b"U2RG")
        stream.write(
            struct.pack(
                "<IIII", 1, ENTITY_POOL_OFFSET, pool_size, BATTLE_TICK_OFFSET
            )
        )
        while frames < cycle_frames:
            raw_tick = process.read(tick_address, 4)
            if raw_tick is None:
                raise RuntimeError("battle tick became unreadable during probe")
            tick = u32(raw_tick, 0)
            if tick == previous_tick and frames:
                time.sleep(0.0005)
                continue
            if frames == 0 and tick == previous_tick:
                current_pool = pool
            else:
                current_pool = process.read(pool_address, pool_size)
                if current_pool is None:
                    raise RuntimeError("entity pool became unreadable during probe")
            elapsed_ns = int((time.perf_counter() - started) * 1_000_000_000)
            stream.write(struct.pack("<IQ", tick, elapsed_ns))
            stream.write(current_pool)
            previous_tick = tick
            frames += 1
    return {
        "frames": frames,
        "first_tick": first_tick,
        "last_tick": previous_tick,
        "first_action_frame": first_action_frame,
        "elapsed_seconds": time.perf_counter() - started,
    }


def load_capture(path: Path) -> list[bytes]:
    frames: list[bytes] = []
    with path.open("rb") as stream:
        if stream.read(4) != b"U2RG":
            raise RuntimeError("probe capture has an invalid header")
        version, _relative, size, _tick = struct.unpack("<IIII", stream.read(16))
        if version != 1:
            raise RuntimeError("unsupported probe capture version")
        while header := stream.read(12):
            if len(header) != 12:
                raise RuntimeError("truncated probe capture header")
            pool = stream.read(size)
            if len(pool) != size:
                raise RuntimeError("truncated probe capture pool")
            entity = p1_entity(pool)
            if entity is not None:
                frames.append(entity)
    return frames


def stable_mode(values: list[int]) -> tuple[int, float]:
    value, count = Counter(values).most_common(1)[0]
    return value, count / len(values)


def analyze(capture: Path, schedule_path: Path, output: Path) -> dict[str, object]:
    document = json.loads(schedule_path.read_text(encoding="utf-8"))
    frames = load_capture(capture)
    cycle = int(document["cycle_frames"])
    period = int(document["schedule"][1]["on_start"]) if len(document["schedule"]) > 1 else cycle
    on_frames = int(document["schedule"][0]["on_end"]) + 1
    tagged: list[tuple[int, int, bytes]] = []
    for entity in frames:
        cursor = u32(entity, 0x674) % cycle
        tagged.append((cursor // period, cursor % period, entity))

    all_off = [
        entity
        for _phase, local, entity in tagged
        if on_frames + 5 <= local < period - 5
    ]
    results = []
    for item in document["schedule"]:
        phase = int(item["phase"])
        on = [
            entity
            for current_phase, local, entity in tagged
            if current_phase == phase and 5 <= local < on_frames - 5
        ]
        candidates = []
        if on and all_off:
            for offset in range(0, ENTITY_STRIDE, 4):
                on_value, on_confidence = stable_mode([u32(e, offset) for e in on])
                off_value, off_confidence = stable_mode([u32(e, offset) for e in all_off])
                if (
                    on_value != off_value
                    and on_confidence >= 0.90
                    and off_confidence >= 0.90
                ):
                    candidates.append(
                        {
                            "offset": f"0x{offset:03X}",
                            "on": f"0x{on_value:08X}",
                            "off": f"0x{off_value:08X}",
                            "on_confidence": round(on_confidence, 3),
                            "off_confidence": round(off_confidence, 3),
                            "changed_bits": f"0x{on_value ^ off_value:08X}",
                        }
                    )
        results.append(
            {
                "id": item["id"],
                "on_samples": len(on),
                "off_samples": len(all_off),
                "stable_dword_candidates": candidates,
            }
        )
    report = {
        "schema_version": 1,
        "capture": str(capture.resolve()),
        "frames": len(frames),
        "results": results,
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy, run, capture, restore, and analyze a Kuon state probe"
    )
    parser.add_argument(
        "--probe", type=Path, default=ROOT / "captures" / "probe" / "chr023_mv_0.txt"
    )
    parser.add_argument(
        "--schedule",
        type=Path,
        default=ROOT / "captures" / "probe" / "chr023_mv_0.schedule.json",
    )
    args = parser.parse_args()
    probe = args.probe.read_bytes()
    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    cycle_frames = int(schedule["cycle_frames"])
    if sha256_file(INDEX_PATH) != EXPECTED_INDEX_SHA256:
        raise RuntimeError("main data index hash changed; refusing deployment")
    manifest = STEAM_MANIFEST.read_text(encoding="utf-8", errors="replace")
    if '"installdir"\t\t"UNDER NIGHT IN-BIRTH II Sys Celes"' not in manifest:
        raise RuntimeError("Steam app manifest does not point to the pinned UNI2 install")

    close_game(force=True)
    archive_path, entry = locate_entry()
    original = read_entry(archive_path, entry)
    if sha256_bytes(original) != EXPECTED_ENTRY_SHA256:
        raise RuntimeError("Kuon archive entry is not the expected original")
    if len(probe) != len(original):
        raise RuntimeError("probe is not an exact-size replacement")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment = ROOT / "captures" / "probe" / stamp
    experiment.mkdir(parents=True, exist_ok=False)
    backup = experiment / "chr023_mv_0.original.txt"
    backup.write_bytes(original)
    capture = experiment / "probe_capture.bin"
    metadata_path = experiment / "probe_capture.json"
    report_path = experiment / "probe_report.json"
    launched = None
    metadata: dict[str, object] = {
        "started_at": datetime.now().astimezone().isoformat(),
        "archive": str(archive_path),
        "entry_offset": entry.offset,
        "entry_size": entry.stored_size,
        "original_sha256": sha256_bytes(original),
        "probe_sha256": sha256_bytes(probe),
        "restored": False,
    }
    try:
        write_entry(archive_path, entry, probe)
        metadata["deployed"] = True
        launched = subprocess.Popen(
            [str(STEAM_EXE), "-applaunch", STEAM_APP_ID],
            cwd=str(STEAM_EXE.parent),
        )
        pid, process, module, _digest = wait_for_process()
        metadata["pid"] = pid
        with process:
            metadata["capture"] = capture_cycle(
                process, module.base, capture, cycle_frames
            )
    except BaseException as error:
        metadata["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        close_error = None
        try:
            close_game(force=True)
        except BaseException as error:
            close_error = f"{type(error).__name__}: {error}"
        finally:
            try:
                write_entry(archive_path, entry, original)
                metadata["restored"] = read_entry(archive_path, entry) == original
            finally:
                if close_error:
                    metadata["close_error"] = close_error
                metadata["stopped_at"] = datetime.now().astimezone().isoformat()
                metadata_path.write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
                )
    if not metadata["restored"]:
        raise RuntimeError("original Kuon entry was not restored")
    report = analyze(capture, args.schedule, report_path)
    print(f"experiment={experiment.resolve()}")
    print(f"capture_frames={report['frames']}")
    print(f"restored={metadata['restored']}")
    for result in report["results"]:
        print(f"{result['id']}: {len(result['stable_dword_candidates'])} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
