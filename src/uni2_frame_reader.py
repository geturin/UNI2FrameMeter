from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import struct
import time

from uni2_probe import EXPECTED_SHA256, require_process


BATTLE_TICK_OFFSET = 0x596B34
ENTITY_POOL_OFFSET = 0xC34E80
ENTITY_STRIDE = 0xBA4
ENTITY_COUNT = 12
KNOWN_MOVES_PATH = Path(__file__).resolve().parents[1] / "data" / "known_moves.json"


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


@dataclass(frozen=True)
class EntityFrame:
    pool_slot: int
    player_slot: int
    active: bool
    action_active: bool
    state_code: int
    action_frame: int
    hitstop_remaining: int
    timer_01e0: int
    timer_04bc: int
    timer_04fc: int
    timer_0580: int
    flags_06b8: int
    timer_0864: int
    timer_0868: int
    state_08f8: int
    move_descriptor_pointer: int
    move_name: str
    move_input: str
    move_frame: int | None
    move_elapsed: int | None
    frame_phase: str | None
    phase_source: str | None
    animation_frame_pointer: int
    attack_data_pointer: int
    state_label: str


def parse_entity(pool_slot: int, data: bytes) -> EntityFrame:
    label_raw = data[0xACC : 0xACC + 0x40]
    label = label_raw.split(b"\0", 1)[0].decode("ascii", errors="replace")
    return EntityFrame(
        pool_slot=pool_slot,
        player_slot=data[0x438],
        active=bool(data[0x7BC]),
        # +0x1C also stays set for passive states such as crouching. +0x4B0
        # bounded the complete confirmed attack and remained zero in those
        # passive states, so it is the safer action gate for the frame meter.
        action_active=bool(u32(data, 0x4B0)),
        state_code=u32(data, 0x24),
        action_frame=u32(data, 0x674),
        hitstop_remaining=u32(data, 0x1E4),
        timer_01e0=u32(data, 0x1E0),
        timer_04bc=u32(data, 0x4BC),
        timer_04fc=u32(data, 0x4FC),
        timer_0580=u32(data, 0x580),
        flags_06b8=u32(data, 0x6B8),
        timer_0864=u32(data, 0x864),
        timer_0868=u32(data, 0x868),
        state_08f8=u32(data, 0x8F8),
        move_descriptor_pointer=u32(data, 0x644),
        move_name="",
        move_input="",
        move_frame=None,
        move_elapsed=None,
        frame_phase=None,
        phase_source=None,
        animation_frame_pointer=u32(data, 0x648),
        attack_data_pointer=u32(data, 0x64C),
        state_label=label,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Read UNI2 battle state once per logic frame")
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--out", default="captures/live_frames.jsonl")
    parser.add_argument(
        "--print-changes",
        action="store_true",
        help="print compact state changes while retaining every frame in JSONL",
    )
    args = parser.parse_args()

    known_document = json.loads(KNOWN_MOVES_PATH.read_text(encoding="utf-8"))
    known_moves = {
        move_name: profile
        for character in known_document.values()
        for move_name, profile in character.items()
    }

    pid, process, module, digest = require_process()
    with process:
        if digest != EXPECTED_SHA256:
            raise RuntimeError("uni2.exe SHA-256 does not match this research profile")

        tick_address = module.base + BATTLE_TICK_OFFSET
        pool_address = module.base + ENTITY_POOL_OFFSET
        pool_size = ENTITY_STRIDE * ENTITY_COUNT
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)

        started = time.perf_counter()
        previous_tick: int | None = None
        previous_compact: tuple | None = None
        move_name_cache: dict[int, str] = {}
        # player_slot -> (first observed tick, previous action frame,
        #                 has shown attack data)
        tracked_moves: dict[int, tuple[int, int, bool]] = {}
        frames = 0
        with destination.open("w", encoding="utf-8", newline="\n") as stream:
            while time.perf_counter() - started < args.duration:
                tick_raw = process.read(tick_address, 4)
                if tick_raw is None:
                    raise RuntimeError("unable to read battle tick")
                tick = u32(tick_raw, 0)
                if tick == previous_tick:
                    time.sleep(0.0005)
                    continue

                pool = process.read(pool_address, pool_size)
                if pool is None:
                    raise RuntimeError("unable to read battle entity pool")
                entities = []
                for slot in range(ENTITY_COUNT):
                    start = slot * ENTITY_STRIDE
                    entity = parse_entity(slot, pool[start : start + ENTITY_STRIDE])
                    if entity.active:
                        pointer = entity.move_descriptor_pointer
                        if pointer not in move_name_cache:
                            raw_name = process.read(pointer, 0x10) if pointer else None
                            if raw_name is None:
                                move_name_cache[pointer] = ""
                            else:
                                move_name_cache[pointer] = raw_name.split(b"\0", 1)[0].decode(
                                    "cp932", errors="replace"
                                )
                        entity = EntityFrame(
                            **{
                                **asdict(entity),
                                "move_name": move_name_cache[pointer],
                            }
                        )
                        profile = known_moves.get(entity.move_name)
                        if not entity.action_active:
                            tracked_moves.pop(entity.player_slot, None)
                        else:
                            tracked = tracked_moves.get(entity.player_slot)
                            if (
                                tracked is None
                                or tick < tracked[0]
                                or entity.action_frame < tracked[1]
                            ):
                                tracked = (tick, entity.action_frame, False)
                            attack_seen = tracked[2] or bool(entity.attack_data_pointer)
                            tracked = (tracked[0], entity.action_frame, attack_seen)
                            tracked_moves[entity.player_slot] = tracked
                            move_frame = entity.action_frame
                            move_elapsed = tick - tracked[0] + 1
                            if entity.hitstop_remaining:
                                phase = "hitstop"
                            elif entity.attack_data_pointer:
                                phase = "active"
                            elif attack_seen:
                                phase = "inactive_after_active"
                            else:
                                phase = "startup_or_nonattack"
                            phase_source = "runtime"
                            move_input = "" if profile is None else str(profile["input"])
                            entity = EntityFrame(
                                **{
                                    **asdict(entity),
                                    "move_input": move_input,
                                    "move_frame": move_frame,
                                    "move_elapsed": move_elapsed,
                                    "frame_phase": phase,
                                    "phase_source": phase_source,
                                }
                            )
                        entities.append(entity)
                entities.sort(key=lambda item: (item.player_slot, item.pool_slot))

                record = {
                    "tick": tick,
                    "time": time.perf_counter() - started,
                    "entities": [asdict(entity) for entity in entities],
                }
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")
                frames += 1
                previous_tick = tick

                compact = tuple(
                    (
                        item.player_slot,
                        item.state_code,
                        item.move_name,
                        item.move_frame,
                        item.frame_phase,
                        item.timer_01e0,
                        item.timer_0864,
                        item.timer_0868,
                        item.flags_06b8,
                    )
                    for item in entities
                )
                if args.print_changes and compact != previous_compact:
                    print(f"tick={tick} {compact}", flush=True)
                previous_compact = compact

        print(f"frames={frames} output={destination.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
