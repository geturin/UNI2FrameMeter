from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from disassemble_xrefs import Pe32


ASCII = re.compile(rb"[\x20-\x7e]{4,}")
CONSTANT = re.compile(r"^_[A-Za-z][A-Za-z0-9_]{2,}$")
REFERENCE = re.compile(r"\b_[A-Za-z][A-Za-z0-9_]{2,}\b")


def group_name(name: str) -> str:
    parts = name.split("_")
    return parts[1] if len(parts) > 2 else "ungrouped"


def immediate_before_string_push(data: bytes, operand_offset: int) -> int | None:
    """Read `push value; push <name>` registration sequences."""

    string_push = operand_offset - 1
    if string_push < 1 or data[string_push] != 0x68:
        return None
    previous = string_push
    if previous >= 2 and data[previous - 2] == 0x6A:
        return data[previous - 1]
    if previous >= 5 and data[previous - 5] == 0x68:
        return struct.unpack_from("<I", data, previous - 4)[0]
    return None


def stack_value_before_string_push(data: bytes, operand_offset: int) -> int | None:
    """Read the alternate `local=value; push &local; push <name>` form."""

    start = max(0, operand_offset - 40)
    window = data[start:operand_offset]
    candidates: list[tuple[int, int]] = []
    # mov dword ptr [ebp+disp8], imm32
    for match in re.finditer(rb"\xC7\x45.(....)", window, re.DOTALL):
        candidates.append((match.start(), struct.unpack("<I", match.group(1))[0]))
    # mov dword ptr [ebp+disp32], imm32
    for match in re.finditer(rb"\xC7\x85....(....)", window, re.DOTALL):
        candidates.append((match.start(), struct.unpack("<I", match.group(1))[0]))
    return max(candidates)[1] if candidates else None


def script_usage_counts(root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in root.rglob("*.txt"):
        text = path.read_text(encoding="cp932", errors="ignore")
        counts.update(REFERENCE.findall(text))
    return counts


def extract(exe: Path, scripts: Path) -> dict[str, object]:
    pe = Pe32(exe)
    usage = script_usage_counts(scripts)
    constants: list[dict[str, object]] = []
    seen: set[str] = set()
    for match in ASCII.finditer(pe.data):
        name = match.group().decode("ascii")
        if not CONSTANT.fullmatch(name) or name in seen:
            continue
        mapped = pe.offset_to_va(match.start())
        if mapped is None:
            continue
        name_va, _section = mapped
        xrefs = pe.absolute_xrefs(name_va)
        evidence = []
        values = []
        for operand_offset, operand_va, section in xrefs:
            value = immediate_before_string_push(pe.data, operand_offset)
            form = "push_immediate"
            if value is None:
                value = stack_value_before_string_push(pe.data, operand_offset)
                form = "stack_value" if value is not None else "unknown"
            evidence.append(
                {
                    "xref_va": operand_va,
                    "xref_rva": operand_va - pe.image_base,
                    "section": section.name,
                    "form": form,
                    "value": value,
                }
            )
            if value is not None:
                values.append(value)
        constants.append(
            {
                "name": name,
                "group": group_name(name),
                "string_file_offset": match.start(),
                "string_rva": name_va - pe.image_base,
                "values": sorted(set(values)),
                "script_uses": usage[name],
                "evidence": evidence,
            }
        )
        seen.add(name)
    constants.sort(key=lambda item: (str(item["group"]), str(item["name"])))
    return {
        "schema": 1,
        "exe": str(exe),
        "groups": dict(Counter(str(item["group"]) for item in constants)),
        "constants": constants,
    }


def markdown(document: dict[str, object]) -> str:
    constants = document["constants"]
    assert isinstance(constants, list)
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in constants:
        assert isinstance(item, dict)
        grouped.setdefault(str(item["group"]), []).append(item)
    lines = [
        "# UNI2 VM constant catalog",
        "",
        "Generated from the pinned executable's VM registration strings. `value` is",
        "decoded from the registration instruction when its form is recognized; blank",
        "values remain unresolved and must not be guessed.",
        "",
        f"Total constants: {len(constants)}",
        "",
        "| Group | Count | Used by extracted scripts | Values decoded |",
        "|---|---:|---:|---:|",
    ]
    for group, items in sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        lines.append(
            f"| `{group}` | {len(items)} | "
            f"{sum(int(item['script_uses']) > 0 for item in items)} | "
            f"{sum(bool(item['values']) for item in items)} |"
        )
    for group, items in sorted(grouped.items()):
        lines.extend(
            [
                "",
                f"## {group}",
                "",
                "| Name | Value | Script uses | Registration RVA |",
                "|---|---:|---:|---:|",
            ]
        )
        for item in items:
            values = item["values"]
            value_text = ", ".join(f"`0x{int(value):X}`" for value in values) if values else ""
            evidence = item["evidence"]
            rvas = ", ".join(
                f"`0x{int(record['xref_rva']):X}`"
                for record in evidence
                if record["section"] == ".text"
            )
            lines.append(
                f"| `{item['name']}` | {value_text} | {item['script_uses']} | {rvas} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("--scripts", type=Path, default=ROOT / "extracted" / "data")
    parser.add_argument("--json", type=Path, default=ROOT / "analysis" / "vm_constants.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "analysis" / "vm_constants.md")
    args = parser.parse_args()
    document = extract(args.exe, args.scripts)
    args.json.write_text(json.dumps(document, indent=2), encoding="utf-8")
    args.markdown.write_text(markdown(document), encoding="utf-8")
    print(f"constants={len(document['constants'])}")
    print(f"json={args.json.resolve()}")
    print(f"markdown={args.markdown.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
