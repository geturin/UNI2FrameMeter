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


IDENTIFIER = re.compile(rb"[A-Za-z][A-Za-z0-9_]{2,}\x00")
SCRIPT_API = re.compile(
    r"\b(BMvCore|BMvEff|BMvTbl|BCMDTbl|BtlPl|BtlOb)\.([A-Za-z_][A-Za-z0-9_]*)"
)

# Contiguous native registration string blocks in the pinned executable.
BLOCKS = {
    "BMvCore": (0x553300, 0x553554),
    "BMvEff": (0x553C00, 0x554700),
    "BMvTbl": (0x555A00, 0x557394),
    "BCMDTbl": (0x558160, 0x558214),
}


def script_usage(root: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in root.rglob("*.txt"):
        text = path.read_text(encoding="cp932", errors="ignore")
        counts.update(".".join(match) for match in SCRIPT_API.findall(text))
    return counts


def wrapper_before_registration(data: bytes, operand_offset: int) -> int | None:
    # Native method registrations store a wrapper address in an ebp local,
    # then pass &local followed by the method-name string.
    start = max(0, operand_offset - 32)
    window = data[start:operand_offset]
    candidates: list[tuple[int, int]] = []
    for match in re.finditer(rb"\xC7\x45.(....)", window, re.DOTALL):
        candidates.append((match.start(), struct.unpack("<I", match.group(1))[0]))
    for match in re.finditer(rb"\xC7\x85....(....)", window, re.DOTALL):
        candidates.append((match.start(), struct.unpack("<I", match.group(1))[0]))
    return max(candidates)[1] if candidates else None


def record_for(pe: Pe32, namespace: str, offset: int, name: str, uses: int) -> dict[str, object] | None:
    mapped = pe.offset_to_va(offset)
    if mapped is None:
        return None
    va, _ = mapped
    evidence = []
    wrappers = []
    for operand_offset, operand_va, section in pe.absolute_xrefs(va):
        if section.name != ".text":
            continue
        wrapper = wrapper_before_registration(pe.data, operand_offset)
        wrapper_mapping = pe.va_to_offset(wrapper) if wrapper else None
        if wrapper_mapping is None or wrapper_mapping[1].name != ".text":
            continue
        evidence.append(
            {
                "registration_rva": operand_va - pe.image_base,
                "wrapper_va": wrapper,
                "wrapper_rva": wrapper - pe.image_base if wrapper else None,
            }
        )
        if wrapper:
            wrappers.append(wrapper)
    if not evidence or not wrappers:
        return None
    return {
        "namespace": namespace,
        "name": name,
        "full_name": f"{namespace}.{name}",
        "string_file_offset": offset,
        "string_rva": va - pe.image_base,
        "wrapper_rvas": sorted({item - pe.image_base for item in wrappers}),
        "script_uses": uses,
        "evidence": evidence,
    }


def extract(exe: Path, scripts: Path) -> dict[str, object]:
    pe = Pe32(exe)
    usage = script_usage(scripts)
    records: dict[str, dict[str, object]] = {}
    for namespace, (start, end) in BLOCKS.items():
        for match in IDENTIFIER.finditer(pe.data, start, end):
            name = match.group()[:-1].decode("ascii")
            if name.startswith("_") or name == namespace:
                continue
            full_name = f"{namespace}.{name}"
            record = record_for(pe, namespace, match.start(), name, usage[full_name])
            if record is not None:
                records.setdefault(full_name, record)

    # Include script-observed namespaces whose registration strings are not in
    # one of the four contiguous blocks above.
    for full_name, uses in usage.items():
        if full_name in records:
            continue
        namespace, name = full_name.split(".", 1)
        needle = name.encode("ascii") + b"\0"
        offset = pe.data.find(needle)
        while offset >= 0:
            record = record_for(pe, namespace, offset, name, uses)
            if record is not None:
                records[full_name] = record
                break
            offset = pe.data.find(needle, offset + 1)

    methods = sorted(records.values(), key=lambda item: (item["namespace"], item["name"]))
    return {
        "schema": 1,
        "exe": str(exe),
        "namespaces": dict(Counter(str(item["namespace"]) for item in methods)),
        "methods": methods,
    }


def markdown(document: dict[str, object]) -> str:
    methods = document["methods"]
    assert isinstance(methods, list)
    lines = [
        "# UNI2 native VM API catalog",
        "",
        "Native VM methods extracted from registration blocks. Wrapper RVAs are",
        "the starting points for tracing storage fields and composite predicates.",
        "",
        f"Total methods: {len(methods)}",
        "",
    ]
    namespaces = sorted({str(item["namespace"]) for item in methods})
    for namespace in namespaces:
        lines.extend(
            [
                f"## {namespace}",
                "",
                "| Method | Wrapper RVA | Script uses |",
                "|---|---:|---:|",
            ]
        )
        for item in methods:
            if item["namespace"] != namespace:
                continue
            wrappers = ", ".join(f"`0x{int(rva):X}`" for rva in item["wrapper_rvas"])
            lines.append(f"| `{item['name']}` | {wrappers} | {item['script_uses']} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("--scripts", type=Path, default=ROOT / "extracted" / "data")
    parser.add_argument("--json", type=Path, default=ROOT / "analysis" / "vm_apis.json")
    parser.add_argument("--markdown", type=Path, default=ROOT / "analysis" / "vm_apis.md")
    args = parser.parse_args()
    document = extract(args.exe, args.scripts)
    args.json.write_text(json.dumps(document, indent=2), encoding="utf-8")
    args.markdown.write_text(markdown(document), encoding="utf-8")
    print(f"methods={len(document['methods'])} namespaces={document['namespaces']}")
    print(f"json={args.json.resolve()}")
    print(f"markdown={args.markdown.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
