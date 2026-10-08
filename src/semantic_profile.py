"""Load current built-in predicates while preserving user display choices.

The JSON shipped inside the application is the single source of default
colors and field definitions. Adjacent/custom profiles may retain their
colors, display switches, timeline settings and additional user attributes;
built-in predicates and confirmation status follow the application version.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any


def bundled_profile() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "frame_semantics.json"
    return Path(__file__).resolve().parents[1] / "frame_semantics.json"


def _read(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schema_version") != 2:
        raise ValueError("unsupported frame-semantics profile schema")
    return document


def load_profile(path: Path) -> dict[str, Any]:
    document = _read(path)
    baseline_path = bundled_profile()
    if not baseline_path.is_file() or path.resolve() == baseline_path.resolve():
        return document
    baseline = _read(baseline_path)
    merged = deepcopy(document)
    styles = merged.setdefault("tokens", {})
    if not isinstance(styles, dict):
        raise ValueError("frame-semantics tokens must be an object")
    for token, default_style in baseline.get("tokens", {}).items():
        current_style = styles.get(token, {})
        if not isinstance(current_style, dict):
            raise ValueError(f"frame-semantics style is not an object: {token}")
        styles[token] = {**deepcopy(default_style), **current_style}
    for section in ("external_attributes", "runtime_attributes"):
        previous = merged.get(section, [])
        if not isinstance(previous, list):
            raise ValueError(f"frame-semantics {section} must be a list")
        current = {
            str(item["token"]): item
            for item in previous
            if isinstance(item, dict) and "token" in item
        }
        definitions: list[dict[str, Any]] = []
        for definition in baseline.get(section, []):
            updated = deepcopy(definition)
            saved = current.pop(str(definition["token"]), None)
            if saved is not None:
                updated["display"] = bool(saved.get("display", updated.get("display", False)))
            # A previous editable profile must not re-enable an incomplete
            # built-in predicate, including the shelved partial CS check.
            if updated.get("status") != "confirmed":
                updated["display"] = False
            definitions.append(updated)
        definitions.extend(current.values())
        merged[section] = definitions
    return merged
