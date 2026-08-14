from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
EXTRACTED = ROOT / "extracted" / "data"

# These domains describe rules or runtime state that can affect battle logic.
# Everything outside the set remains available in vm_constants.json; keeping the
# boundary explicit prevents a UI-oriented shortlist from becoming the source of
# truth accidentally.
BATTLE_DOMAINS = {
    "Angle",
    "AsFlag",
    "AtkFlag",
    "CancelFlag",
    "CaptureHitFlag",
    "CatchFlag",
    "CatchSuccess",
    "CharaMoveMode",
    "CharaPrio",
    "ClearFlag",
    "Direction",
    "Exist",
    "ExistMode",
    "FrameFlagEx",
    "GetPos",
    "GuardFlag",
    "HC",
    "Han6Hantei",
    "Hantei",
    "HanteiFlag",
    "HitCheckFlag",
    "HitType",
    "ImpactFlag",
    "InterruptType",
    "KOMode",
    "LiberateType",
    "MODE",
    "MoveCode0",
    "MvStFlag",
    "ObjFlags",
    "ObjProcFlag",
    "ObjProcFlags",
    "ObjType",
    "PAniFlag",
    "PAniFrame",
    "PCGaugeType",
    "PartnerFlag",
    "PosState",
    "Position",
    "PrioType",
    "SkillCount",
    "SkillType",
    "SpCommandFlag",
    "SpGauge",
    "SpGaugeMode",
    "State",
    "Status",
    "StatusFlag0",
    "StatusFlag1",
    "ThrowRelease",
    "ThrowType",
    "VecFlag",
    "Vector",
    "defBtlFinish",
    "eWinType",
}

# APIs are included by capability, not by whether the current overlay uses them.
# The broad verbs intentionally retain gauge, object, damage and character-local
# state interfaces: those are where persistent buffs and debuffs are implemented.
STATE_API_RE = re.compile(
    r"(?:Flag|Status|State|Cancel|Guard|Hit|Attack|Damage|Bound|Capture|Catch|"
    r"Throw|Ukemi|Armor|Hosei|Recover|Moveable|Muteki|Exist|StopTime|Skill|"
    r"Gauge|GRD|Liberate|Count|Timer|Alive|Down|Landing|PP|LP|SP|Power|Prio|"
    r"Vector|Muki|Position|Scale|Finalize|Spark|Air|Wall|Kasanari)",
    re.IGNORECASE,
)

PP_CALL_RE = re.compile(
    r"BMvTbl\.(?:GetPP|SetPP|AddPP)\s*\(\s*([A-Za-z_]\w*|[-+]?\d+)",
)
PP_FLAG_RE = re.compile(r"\b(?:def_PPFlag|Def_PPFlag|CDef_\w*PPFlag)_[A-Za-z0-9_]+\b")
CUSTOM_STATE_RE = re.compile(
    r"\b(?:def|Def|CDef)_[A-Za-z0-9_]*(?:Flag|Flags|Status|State|Mode|Timer|"
    r"Gauge|Stock|Count|Level|Lv|Power|Charge|Mark|Buff|Debuff)[A-Za-z0-9_]*\b"
)


def read_script(path: Path) -> str:
    return path.read_bytes().decode("cp932", errors="replace")


def script_files() -> list[Path]:
    return sorted(EXTRACTED.glob("chr*/chr*_*.txt")) + [EXTRACTED / "_combase.txt"]


def occurrences(pattern: re.Pattern[str]) -> tuple[dict[str, int], dict[str, list[str]]]:
    counts: Counter[str] = Counter()
    files: defaultdict[str, set[str]] = defaultdict(set)
    for path in script_files():
        if not path.is_file():
            continue
        text = read_script(path)
        for match in pattern.finditer(text):
            symbol = match.group(1) if match.lastindex else match.group(0)
            counts[symbol] += 1
            files[symbol].add(path.relative_to(ROOT).as_posix())
    return dict(sorted(counts.items())), {
        key: sorted(value) for key, value in sorted(files.items())
    }


def parse_bound_effects() -> list[dict[str, object]]:
    path = EXTRACTED / "BoundEff.txt"
    text = read_script(path)
    assignments = list(re.finditer(r"st\[(\d+)\]\s*=\s*//\s*([^\r\n]*)", text))
    effects: list[dict[str, object]] = []
    for index, match in enumerate(assignments):
        start = match.end()
        end = assignments[index + 1].start() if index + 1 < len(assignments) else len(text)
        body = text[start:end]
        fields: dict[str, object] = {}
        for key in ("times", "effinterval", "effpos", "colortype", "colorinterval"):
            value = re.search(rf"\b{key}\s*=\s*(-?\d+)", body)
            if value:
                fields[key] = int(value.group(1))
        effects.append(
            {
                "slot": int(match.group(1)),
                "comment_ja": match.group(2).strip(),
                **fields,
                "source": path.relative_to(ROOT).as_posix(),
            }
        )
    assigned = {int(effect["slot"]) for effect in effects}
    for slot in range(16):
        if slot not in assigned:
            effects.append(
                {
                    "slot": slot,
                    "comment_ja": "unassigned/default",
                    "source": path.relative_to(ROOT).as_posix(),
                }
            )
    return sorted(effects, key=lambda effect: int(effect["slot"]))


def main() -> int:
    constants_doc = json.loads((ANALYSIS / "vm_constants.json").read_text(encoding="utf-8"))
    apis_doc = json.loads((ANALYSIS / "vm_apis.json").read_text(encoding="utf-8"))

    battle_constants = [
        {**item, "evidence_state": "name_value_only"}
        for item in constants_doc["constants"]
        if item["group"] in BATTLE_DOMAINS
    ]
    other_constants = [
        {
            **item,
            "evidence_state": "cataloged_non_battle_or_unclassified",
        }
        for item in constants_doc["constants"]
        if item["group"] not in BATTLE_DOMAINS
    ]
    state_apis = [
        {**item, "evidence_state": "registered_wrapper"}
        for item in apis_doc["methods"]
        if STATE_API_RE.search(item["name"])
    ]
    other_apis = [
        {**item, "evidence_state": "cataloged_non_state_or_unclassified"}
        for item in apis_doc["methods"]
        if not STATE_API_RE.search(item["name"])
    ]

    pp_counts, pp_files = occurrences(PP_CALL_RE)
    flag_counts, flag_files = occurrences(PP_FLAG_RE)
    custom_counts, custom_files = occurrences(CUSTOM_STATE_RE)
    pp_slots = [
        {"symbol": symbol, "uses": uses, "files": pp_files[symbol]}
        for symbol, uses in pp_counts.items()
    ]
    pp_flags = [
        {"symbol": symbol, "uses": uses, "files": flag_files[symbol]}
        for symbol, uses in flag_counts.items()
    ]
    custom_symbols = [
        {"symbol": symbol, "uses": uses, "files": custom_files[symbol]}
        for symbol, uses in custom_counts.items()
    ]

    result = {
        "schema": 1,
        "scope": {
            "vm_constants_total": len(constants_doc["constants"]),
            "vm_apis_total": len(apis_doc["methods"]),
            "battle_rule_domains": sorted(BATTLE_DOMAINS),
            "battle_constants": len(battle_constants),
            "other_or_unclassified_constants": len(other_constants),
            "state_related_apis": len(state_apis),
            "other_or_unclassified_apis": len(other_apis),
            "character_pp_slots_referenced": len(pp_slots),
            "character_pp_flag_symbols": len(pp_flags),
            "character_state_like_symbols": len(custom_symbols),
            "bound_effect_slots": 16,
        },
        "battle_constants": battle_constants,
        "other_or_unclassified_constants": other_constants,
        "state_related_apis": state_apis,
        "other_or_unclassified_apis": other_apis,
        "character_pp_slots": pp_slots,
        "character_pp_flags": pp_flags,
        "character_state_symbols": custom_symbols,
        "bound_effects": parse_bound_effects(),
        "notes": [
            "No single flat status enum exists; this file is the union catalog.",
            "Character PP symbols are semantic names referenced by scripts; their numeric slot bindings still require native/global-table tracing.",
            "Name/value or registered-wrapper evidence does not prove the final per-frame predicate.",
        ],
    }
    output_json = ANALYSIS / "battle_state_catalog.json"
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    groups = Counter(item["group"] for item in battle_constants)
    lines = [
        "# UNI2 exhaustive battle-state catalog",
        "",
        "This is an engine-derived union catalog, not the overlay display list. Unknown",
        "items remain listed until their final native predicate has been decoded.",
        "",
        "## Coverage",
        "",
    ]
    for key, value in result["scope"].items():
        if key == "battle_rule_domains":
            continue
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Engine rule domains", "", "| Domain | Members |", "|---|---:|"])
    for group, count in sorted(groups.items()):
        lines.append(f"| `{group}` | {count} |")
    lines.extend(
        [
            "",
            "## Engine gameplay constants (all items)",
            "",
            "| Domain | Constant | Registered value(s) | Script uses |",
            "|---|---|---|---:|",
        ]
    )
    for item in battle_constants:
        values = ", ".join(f"`0x{value & 0xFFFFFFFF:X}`" for value in item["values"])
        lines.append(
            f"| `{item['group']}` | `{item['name']}` | {values or 'unresolved'} | "
            f"{item['script_uses']} |"
        )
    lines.extend(
        [
            "",
            "## State-related native VM APIs (all items)",
            "",
            "| API | Wrapper RVA(s) | Script uses |",
            "|---|---|---:|",
        ]
    )
    for item in state_apis:
        wrappers = ", ".join(f"`0x{value:X}`" for value in item["wrapper_rvas"])
        lines.append(
            f"| `{item['full_name']}` | {wrappers or 'unresolved'} | "
            f"{item['script_uses']} |"
        )
    lines.extend(
        [
            "",
            "## Character-owned state",
            "",
            "The scripts access character-specific persistent state through PP slots. These",
            "cannot be reduced to the engine `_Status` enum. The JSON catalog records every",
            "referenced slot, PP flag and state-like symbol together with source files.",
            "",
            "### PP slots referenced by scripts",
            "",
            "| Symbol/index | Uses | Character files |",
            "|---|---:|---|",
        ]
    )
    for item in pp_slots:
        files = ", ".join(sorted({Path(path).parent.name for path in item["files"]}))
        lines.append(f"| `{item['symbol']}` | {item['uses']} | {files} |")
    lines.extend(
        [
            "",
            "### PP bit flags referenced by scripts",
            "",
            "| Symbol | Uses | Character files |",
            "|---|---:|---|",
        ]
    )
    for item in pp_flags:
        files = ", ".join(sorted({Path(path).parent.name for path in item["files"]}))
        lines.append(f"| `{item['symbol']}` | {item['uses']} | {files} |")
    lines.extend(
        [
            "",
            "### Other character state-like symbols",
            "",
            "| Symbol | Uses | Character files |",
            "|---|---:|---|",
        ]
    )
    for item in custom_symbols:
        files = ", ".join(sorted({Path(path).parent.name for path in item["files"]}))
        lines.append(f"| `{item['symbol']}` | {item['uses']} | {files} |")
    lines.extend(
        [
            "",
            "## Bound/status-effect table",
            "",
            "| Slot | Definition | Duration | Effect interval |",
            "|---:|---|---:|---:|",
        ]
    )
    for effect in result["bound_effects"]:
        lines.append(
            f"| {effect['slot']} | {effect['comment_ja']} | "
            f"{effect.get('times', '')} | {effect.get('effinterval', '')} |"
        )
    lines.extend(
        [
            "",
            "## Evidence warning",
            "",
            "The complete item-level records are in `battle_state_catalog.json`. A name is",
            "not marked display-safe merely because it appears here: setter storage, lifetime,",
            "descriptor fallback and final consumer must be traced independently.",
            "",
        ]
    )
    (ANALYSIS / "battle_state_catalog.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result["scope"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
