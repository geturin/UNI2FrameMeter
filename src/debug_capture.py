from __future__ import annotations

import json
from pathlib import Path
import struct
import time
from datetime import datetime
from typing import BinaryIO, TextIO


class DebugCapture:
    """Toggleable, logic-frame-synchronised entity-pool capture."""

    def __init__(
        self,
        directory: Path,
        region_offset: int,
        region_size: int,
        tick_offset: int,
        image_sha256: str,
        build_id: str,
        display_mode: str,
    ) -> None:
        self.directory = directory
        self.region_offset = region_offset
        self.region_size = region_size
        self.tick_offset = tick_offset
        self.image_sha256 = image_sha256
        self.build_id = build_id
        self.display_mode = display_mode
        self.binary: BinaryIO | None = None
        self.events: TextIO | None = None
        self.binary_path: Path | None = None
        self.events_path: Path | None = None
        self.started_at = ""
        self.started_perf = 0.0
        self.frames = 0
        self.first_tick: int | None = None
        self.last_tick: int | None = None

    @property
    def active(self) -> bool:
        return self.binary is not None

    def toggle(self) -> Path | None:
        if self.active:
            return self.stop()
        return self.start()

    def start(self) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        stem = self.directory / f"uni2_debug_{stamp}"
        self.binary_path = stem.with_suffix(".bin")
        self.events_path = stem.with_suffix(".jsonl")
        self.binary = self.binary_path.open("wb")
        self.events = self.events_path.open("w", encoding="utf-8", newline="\n")
        self.binary.write(b"U2RG")
        self.binary.write(
            struct.pack(
                "<IIII",
                1,
                self.region_offset,
                self.region_size,
                self.tick_offset,
            )
        )
        self.started_at = datetime.now().astimezone().isoformat()
        self.started_perf = time.perf_counter()
        self.frames = 0
        self.first_tick = None
        self.last_tick = None
        return self.binary_path

    def record(self, tick: int, pool: bytes, event: dict[str, object]) -> None:
        if self.binary is None or self.events is None:
            return
        elapsed_ns = int((time.perf_counter() - self.started_perf) * 1_000_000_000)
        self.binary.write(struct.pack("<IQ", tick, elapsed_ns))
        self.binary.write(pool)
        self.events.write(
            json.dumps(
                {"tick": tick, "elapsed_ns": elapsed_ns, **event},
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n"
        )
        self.frames += 1
        if self.first_tick is None:
            self.first_tick = tick
        self.last_tick = tick

    def stop(self) -> Path | None:
        if self.binary is None:
            return None
        binary_path = self.binary_path
        assert binary_path is not None
        events_path = self.events_path
        self.binary.close()
        self.binary = None
        if self.events is not None:
            self.events.close()
            self.events = None
        metadata = {
            "started_at": self.started_at,
            "stopped_at": datetime.now().astimezone().isoformat(),
            "image_sha256": self.image_sha256,
            "overlay_build": self.build_id,
            "display_mode": self.display_mode,
            "tick_offset": self.tick_offset,
            "region_offset": self.region_offset,
            "region_size": self.region_size,
            "frames": self.frames,
            "first_tick": self.first_tick,
            "last_tick": self.last_tick,
            "binary": str(binary_path.resolve()),
            "events": str(events_path.resolve()) if events_path else None,
        }
        binary_path.with_suffix(".json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return binary_path

