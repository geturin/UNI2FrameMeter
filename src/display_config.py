from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class DisplayItem:
    token: str
    display: bool
    status: str


class DisplayConfig:
    """Read and persist only the user-facing display switches."""

    def __init__(self, path: Path, document: dict[str, object]) -> None:
        self.path = path
        self.document = document

    @classmethod
    def load(cls, path: Path) -> "DisplayConfig":
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("schema_version") != 2:
            raise ValueError("unsupported frame-semantics profile schema")
        return cls(path, document)

    def items(self) -> tuple[DisplayItem, ...]:
        result: list[DisplayItem] = []
        seen: set[str] = set()
        for section in ("external_attributes", "runtime_attributes"):
            raw_items = self.document.get(section, [])
            if not isinstance(raw_items, list):
                continue
            for raw in raw_items:
                if not isinstance(raw, dict) or "token" not in raw:
                    continue
                token = str(raw["token"])
                if token in seen:
                    continue
                seen.add(token)
                result.append(
                    DisplayItem(
                        token=token,
                        display=bool(raw.get("display", False)),
                        status=str(raw.get("status", "incomplete")),
                    )
                )
        return tuple(result)

    def set_display(self, token: str, display: bool) -> None:
        found = False
        for section in ("external_attributes", "runtime_attributes"):
            raw_items = self.document.get(section, [])
            if not isinstance(raw_items, list):
                continue
            for raw in raw_items:
                if not isinstance(raw, dict) or raw.get("token") != token:
                    continue
                if display and raw.get("status") != "confirmed":
                    raise ValueError(f"cannot display unconfirmed attribute: {token}")
                raw["display"] = bool(display)
                found = True
        if not found:
            raise KeyError(token)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        temporary.write_text(
            json.dumps(self.document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)
