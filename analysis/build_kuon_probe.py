from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "extracted" / "data" / "chr023" / "chr023_mv_0.txt"
DEFAULT_MANIFEST = ROOT / "data" / "kuon_probe_states.json"


def strip_comments(source: str) -> str:
    """Remove Squirrel comments while preserving strings and line boundaries."""
    output: list[str] = []
    index = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            if char in "\r\n":
                line_comment = False
                output.append(char)
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
                continue
            if char in "\r\n":
                output.append(char)
            index += 1
            continue
        if quote:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in "\"'":
            quote = char
            output.append(char)
            index += 1
            continue
        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        output.append(char)
        index += 1
    if quote or block_comment:
        raise ValueError("unterminated string or block comment in source")
    return "".join(output)


def make_probe_body(document: dict[str, object]) -> tuple[str, list[dict[str, object]]]:
    on_frames = int(document["on_frames"])
    off_frames = int(document["off_frames"])
    states = list(document["states"])
    if on_frames <= 0 or off_frames < 1 or not states:
        raise ValueError("probe schedule requires states, positive on_frames and off_frames")
    period = on_frames + off_frames
    total = period * len(states)
    lines = [
        "\t\tlocal __probe_frame=BMvTbl.GetMvStatus().MvCount%" + str(total) + ";",
        "\t\tlocal __probe_phase=__probe_frame/" + str(period) + ";",
        "\t\tlocal __probe_local=__probe_frame%" + str(period) + ";",
        "\t\tif(__probe_local<" + str(on_frames) + ")",
        "\t\t{",
    ]
    schedule: list[dict[str, object]] = []
    for phase, item in enumerate(states):
        statement = str(item["apply"]).strip()
        prefix = "if" if phase == 0 else "else if"
        lines.append(f"\t\t\t{prefix}(__probe_phase=={phase}){{{statement}}}")
        start = phase * period
        schedule.append(
            {
                "phase": phase,
                "id": item["id"],
                "kind": item.get("kind", "direct"),
                "on_start": start,
                "on_end": start + on_frames - 1,
                "off_start": start + on_frames,
                "off_end": start + period - 1,
            }
        )
    lines.append("\t\t}")
    return "\r\n".join(lines) + "\r\n", schedule


def inject_neutral(source: str, body: str) -> str:
    marker = "t.Mv_Neutral <-"
    start = source.find(marker)
    if start < 0:
        raise ValueError("Mv_Neutral table was not found")
    function = source.find("function FrameUpdate_After()", start)
    if function < 0:
        raise ValueError("Mv_Neutral.FrameUpdate_After was not found")
    opening = source.find("{", function)
    closing = source.find("}", opening)
    if opening < 0 or closing < 0:
        raise ValueError("Mv_Neutral.FrameUpdate_After braces were not found")
    if source[opening + 1 : closing].strip():
        raise ValueError("Mv_Neutral.FrameUpdate_After is no longer empty")
    return source[: opening + 1] + "\r\n" + body + "\t" + source[closing:]


def build(source_path: Path, manifest_path: Path, output_path: Path) -> dict[str, object]:
    original = source_path.read_bytes()
    source = original.decode("cp932")
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1:
        raise ValueError("unsupported probe manifest schema")
    body, schedule = make_probe_body(document)
    modified = inject_neutral(strip_comments(source), body).encode("cp932")
    if len(modified) > len(original):
        raise ValueError(
            f"probe source exceeds fixed entry size by {len(modified) - len(original)} bytes"
        )
    modified += b"\r\n" + b" " * (len(original) - len(modified) - 2)
    if len(modified) != len(original):
        raise RuntimeError("fixed-size probe padding failed")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(modified)
    schedule_path = output_path.with_suffix(".schedule.json")
    schedule_document = {
        "schema_version": 1,
        "source_size": len(original),
        "probe_size": len(modified),
        "cycle_frames": (int(document["on_frames"]) + int(document["off_frames"]))
        * len(schedule),
        "counter": "BMvTbl.GetMvStatus().MvCount",
        "schedule": schedule,
    }
    schedule_path.write_text(
        json.dumps(schedule_document, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return schedule_document


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a fixed-size Kuon state probe")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    schedule = build(args.source, args.manifest, args.out)
    print(f"probe={args.out.resolve()}")
    print(f"bytes={schedule['probe_size']}")
    print(f"cycle_frames={schedule['cycle_frames']}")
    print(f"states={len(schedule['schedule'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
