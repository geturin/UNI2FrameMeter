from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def i32s(data: bytes, offset: int, count: int) -> tuple[int, ...]:
    return struct.unpack_from(f"<{count}i", data, offset)


def frame_tags(frame: bytes) -> dict[str, int]:
    result: dict[str, int] = {}
    # These are confirmed HA6 record markers. Values remain deliberately raw
    # until each tag's engine meaning has been validated against runtime data.
    for tag in (
        b"AFPR",
        b"AFHK",
        b"ATST",
        b"ATGD",
        b"ATHE",
        b"ATSP",
        b"ATHH",
        b"ATF1",
        b"ATAT",
        b"ATC0",
    ):
        offset = frame.find(tag)
        if offset >= 0 and offset + 8 <= len(frame):
            result[tag.decode("ascii")] = u32(frame, offset + 4)
    return result


def parse_record(data: bytes, start: int, end: int, name: str) -> dict[str, object] | None:
    record = data[start:end]
    descriptor = record.find(b"PDS2")
    if descriptor < 0 or descriptor + 8 > len(record):
        return None
    descriptor_size = u32(record, descriptor + 4)
    if descriptor_size % 4 or descriptor + 8 + descriptor_size > len(record):
        return None
    header = i32s(record, descriptor + 8, descriptor_size // 4)
    frames: list[dict[str, object]] = []
    for index, match in enumerate(re.finditer(b"FSTR", record)):
        frame_end = record.find(b"FEND", match.start() + 4)
        if frame_end < 0:
            break
        tags = frame_tags(record[match.start() : frame_end])
        frames.append({"index": index, "attack": "ATST" in tags, "tags": tags})
    return {
        "name": name,
        "offset": start,
        "header_raw": header,
        "frame_count": len(frames),
        "attack_frames": [frame["index"] for frame in frames if frame["attack"]],
        "frames": frames,
    }


def parse(path: Path) -> list[dict[str, object]]:
    data = path.read_bytes()
    if not data.startswith(b"Hantei6DataFile\0"):
        raise ValueError(f"not an HA6 judgment file: {path}")

    records: list[dict[str, object]] = []

    # Inline/string-table records. This is where the inherited normal attacks
    # (standing weak/medium/strong, etc.) live in chrNNN.ha6.
    for match in re.finditer(b"PSTR", data):
        end = data.find(b"PEND", match.start() + 8)
        if end < 0:
            continue
        block = data[match.start() + 8 : end]
        text_tag = block.find(b"PTT2")
        if text_tag < 0 or text_tag + 8 > len(block):
            continue
        size = u32(block, text_tag + 4)
        raw_name = block[text_tag + 8 : text_tag + 8 + size].split(b"\0", 1)[0]
        name = raw_name.decode("cp932", errors="replace")
        parsed = parse_record(data, match.start(), end, name)
        if parsed is not None:
            parsed["string_id"] = u32(data, match.start() + 4)
            records.append(parsed)

    # Explicit named records. Character-specific moves and projectile/effect
    # judgment records normally use PTCN.
    named = list(re.finditer(b"PTCN", data))
    for index, match in enumerate(named):
        size = u32(data, match.start() + 4)
        raw_name = data[match.start() + 8 : match.start() + 8 + size].rstrip(b"\0")
        name = raw_name.decode("cp932", errors="replace")
        end = named[index + 1].start() if index + 1 < len(named) else len(data)
        parsed = parse_record(data, match.start(), end, name)
        if parsed is not None:
            records.append(parsed)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect raw UNI2 HA6 judgment records")
    parser.add_argument("ha6", type=Path)
    parser.add_argument("--match", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    records = parse(args.ha6)
    pattern = re.compile(args.match, re.IGNORECASE) if args.match else None
    records = [item for item in records if pattern is None or pattern.search(str(item["name"]))]
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    for item in records:
        print(
            f"{item['offset']:08x} {item['name']!r} frames={item['frame_count']} "
            f"attack_frames={item['attack_frames']} header={item['header_raw']}"
        )
        for frame in item["frames"]:
            if frame["attack"]:
                print(f"  frame {frame['index']}: {frame['tags']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
