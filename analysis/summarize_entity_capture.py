from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uni2_probe import EXPECTED_SHA256, require_process  # noqa: E402


ENTITY_STRIDE = 0xBA4


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def text(data: bytes, offset: int, size: int = 0x40) -> str:
    return data[offset : offset + size].split(b"\0", 1)[0].decode(
        "ascii", errors="replace"
    )


@dataclass
class Segment:
    epoch: int
    slot: int
    first_tick: int
    last_tick: int
    descriptor: int
    state_label: str
    state_code: int
    action_type: int
    active_frames: int = 0

    @property
    def frames(self) -> int:
        return self.last_tick - self.first_tick + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a UNI2 entity capture")
    parser.add_argument("capture", type=Path)
    parser.add_argument("--min-frames", type=int, default=1)
    args = parser.parse_args()

    segments: list[Segment] = []
    pointers: set[int] = set()
    current: dict[int, Segment] = {}
    epoch = 0
    previous_tick: int | None = None

    with args.capture.open("rb") as stream:
        if stream.read(4) != b"U2RG":
            raise RuntimeError("not a U2RG capture")
        version, _relative, region_size, _tick_offset = struct.unpack(
            "<IIII", stream.read(16)
        )
        if version != 1:
            raise RuntimeError(f"unsupported capture version {version}")

        while header := stream.read(12):
            if len(header) != 12:
                raise RuntimeError("truncated frame header")
            tick, _elapsed_ns = struct.unpack("<IQ", header)
            region = stream.read(region_size)
            if len(region) != region_size:
                raise RuntimeError("truncated frame data")
            if previous_tick is not None and tick < previous_tick:
                epoch += 1
                current.clear()
            previous_tick = tick

            for slot in range(region_size // ENTITY_STRIDE):
                entity = region[slot * ENTITY_STRIDE : (slot + 1) * ENTITY_STRIDE]
                if not u32(entity, 0x7BC):
                    current.pop(slot, None)
                    continue
                descriptor = u32(entity, 0x644)
                pointers.add(descriptor)
                key = (
                    descriptor,
                    text(entity, 0xACC),
                    u32(entity, 0x24),
                    u32(entity, 0x4B0),
                )
                segment = current.get(slot)
                old_key = None if segment is None else (
                    segment.descriptor,
                    segment.state_label,
                    segment.state_code,
                    segment.action_type,
                )
                if segment is None or key != old_key or tick != segment.last_tick + 1:
                    segment = Segment(epoch, slot, tick, tick, *key)
                    segments.append(segment)
                    current[slot] = segment
                else:
                    segment.last_tick = tick
                if u32(entity, 0x64C):
                    segment.active_frames += 1

    names: dict[int, str] = {}
    pid, process, _module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match")
        for pointer in pointers:
            raw = process.read(pointer, 0x20) if pointer else None
            names[pointer] = (
                raw.split(b"\0", 1)[0].decode("cp932", errors="replace") if raw else ""
            )

    print(f"capture={args.capture} epochs={epoch + 1} segments={len(segments)} pid={pid}")
    print("epoch slot ticks frames active action state descriptor name label")
    for item in segments:
        if item.frames < args.min_frames:
            continue
        if not item.action_type and item.active_frames == 0 and item.frames < 5:
            continue
        print(
            f"{item.epoch:>2} {item.slot} {item.first_tick:>7}-{item.last_tick:<7} "
            f"{item.frames:>4} {item.active_frames:>3} 0x{item.action_type:08x} "
            f"{item.state_code:>2} 0x{item.descriptor:08x} "
            f"{ascii(names.get(item.descriptor, ''))} {ascii(item.state_label)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
