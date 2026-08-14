from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uni2_probe import EXPECTED_SHA256, require_process  # noqa: E402


TICK_OFFSET = 0x596B34
DEFAULT_REGION_OFFSET = 0x850000
DEFAULT_REGION_SIZE = 0x10000


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record a read-only, logic-frame-synchronized UNI2 memory region"
    )
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--duration", type=float, default=12.0)
    parser.add_argument("--relative", type=lambda value: int(value, 0), default=DEFAULT_REGION_OFFSET)
    parser.add_argument("--size", type=lambda value: int(value, 0), default=DEFAULT_REGION_SIZE)
    parser.add_argument("--out", default="captures/light_attack_region.bin")
    args = parser.parse_args()

    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")

        tick_address = module.base + TICK_OFFSET
        region_address = module.base + args.relative
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)

        print(f"ARMED delay={args.delay:.1f}s", flush=True)
        time.sleep(args.delay)
        print("RECORDING", flush=True)

        started = time.perf_counter()
        previous_tick: int | None = None
        frame_count = 0
        with destination.open("wb") as stream:
            stream.write(b"U2RG")
            stream.write(struct.pack("<IIII", 1, args.relative, args.size, TICK_OFFSET))
            while time.perf_counter() - started < args.duration:
                tick_raw = process.read(tick_address, 4)
                if tick_raw is None:
                    raise RuntimeError("unable to read battle tick")
                tick = struct.unpack("<I", tick_raw)[0]
                if tick != previous_tick:
                    data = process.read(region_address, args.size)
                    if data is None:
                        raise RuntimeError("unable to read battle region")
                    elapsed_ns = int((time.perf_counter() - started) * 1_000_000_000)
                    stream.write(struct.pack("<IQ", tick, elapsed_ns))
                    stream.write(data)
                    previous_tick = tick
                    frame_count += 1
                time.sleep(0.0005)

        metadata = {
            "pid": pid,
            "image_sha256": digest,
            "module_base": module.base,
            "tick_offset": TICK_OFFSET,
            "region_offset": args.relative,
            "region_size": args.size,
            "duration": args.duration,
            "frames": frame_count,
            "binary": str(destination.resolve()),
        }
        destination.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        print(f"DONE frames={frame_count} output={destination.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
