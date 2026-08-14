from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from semantic_engine import DEFAULT_PROFILE, SemanticEngine  # noqa: E402
from uni2_frame_reader import ENTITY_COUNT, ENTITY_STRIDE  # noqa: E402


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def replay(path: Path, profile: Path) -> tuple[int, Counter[str]]:
    engine = SemanticEngine(profile=profile)
    counts: Counter[str] = Counter()
    logic_frames = 0
    previous_tick: int | None = None
    with path.open("rb") as stream:
        if stream.read(4) != b"U2RG":
            raise ValueError("not a U2RG capture")
        version, _offset, pool_size, _tick_offset = struct.unpack(
            "<IIII", stream.read(16)
        )
        if version != 1 or pool_size % ENTITY_STRIDE:
            raise ValueError("unsupported capture layout")
        while header := stream.read(12):
            if len(header) != 12:
                raise ValueError("truncated frame header")
            tick, _elapsed_ns = struct.unpack("<IQ", header)
            pool = stream.read(pool_size)
            if len(pool) != pool_size:
                raise ValueError("truncated entity pool")
            if tick == previous_tick:
                continue
            if previous_tick is not None and tick < previous_tick:
                engine.reset()
            previous_tick = tick
            logic_frames += 1
            for slot in range(min(ENTITY_COUNT, pool_size // ENTITY_STRIDE)):
                start = slot * ENTITY_STRIDE
                entity = pool[start : start + ENTITY_STRIDE]
                if not u32(entity, 0x7BC) or entity[0x438] not in (0, 1):
                    continue
                player = entity[0x438]
                frame = engine.classify(entity, player).frame
                for token in frame.codes:
                    if isinstance(token, str):
                        counts[f"P{player + 1}:{token}"] += 1
    return logic_frames, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay UNI2 overlay debug captures")
    parser.add_argument("captures", nargs="*", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_PROFILE)
    args = parser.parse_args()
    paths = args.captures or sorted((ROOT / "log").glob("uni2_debug_*.bin"))
    for path in paths:
        logic_frames, counts = replay(path, args.config)
        cs = {key: value for key, value in counts.items() if key.endswith(":cs_cancel")}
        print(f"{path.name}: logic_frames={logic_frames}; cs={cs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
