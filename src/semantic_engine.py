from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import struct
from typing import Any

from frame_timeline import FrameBands


DEFAULT_PROFILE = Path(__file__).resolve().parents[1] / "data" / "frame_semantics.json"


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def is_actionable(movable: int, state_label: bytes = b"") -> bool:
    return movable != 0 or state_label.startswith(b"Mv_Modori_Guard")


def is_hard_locked(movable: int, state_label: bytes = b"") -> bool:
    return not is_actionable(movable, state_label)


@dataclass(frozen=True)
class EntitySnapshot:
    raw: bytes
    state_code: int
    movable: int
    action_type: int
    action_frame: int
    hitstop: int
    control_state: int
    state_label: bytes

    @classmethod
    def parse(cls, data: bytes) -> "EntitySnapshot":
        return cls(
            raw=data,
            state_code=u32(data, 0x24),
            movable=u32(data, 0x440),
            action_type=u32(data, 0x4B0),
            action_frame=u32(data, 0x674),
            hitstop=u32(data, 0x1E4),
            control_state=u32(data, 0xB6C),
            state_label=data[0xACC:0xB20].split(b"\0", 1)[0],
        )

    @property
    def actionable(self) -> bool:
        return is_actionable(self.movable, self.state_label)


@dataclass(frozen=True)
class RuntimeAttribute:
    token: str
    display: bool
    status: str
    offset: int
    mask: int
    equals: int

    def matches(self, data: bytes) -> bool:
        return u32(data, self.offset) & self.mask == self.equals


@dataclass(frozen=True)
class SemanticResult:
    frame: FrameBands


@dataclass
class PhaseTracker:
    active: bool = False
    last_frame: int = 0
    attack_seen: bool = False

    def reset(self) -> None:
        self.active = False
        self.last_frame = 0
        self.attack_seen = False


class SemanticEngine:
    """Convert each live entity snapshot directly into one display cell."""

    def __init__(self, profile: Path = DEFAULT_PROFILE, raw_states: bool = False):
        document = json.loads(profile.read_text(encoding="utf-8"))
        if document.get("schema_version") != 2:
            raise ValueError("unsupported frame-semantics profile schema")
        self.raw_states = raw_states
        self.token_styles: dict[str, dict[str, Any]] = document["tokens"]
        self.runtime_attributes = tuple(
            RuntimeAttribute(
                token=attribute["token"],
                display=bool(attribute["display"]),
                status=str(attribute["status"]),
                offset=int(attribute["offset"], 0),
                mask=int(attribute["mask"], 0),
                equals=int(attribute["equals"], 0),
            )
            for attribute in document["runtime_attributes"]
        )
        unknown = {
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.token not in self.token_styles
        }
        if unknown:
            raise ValueError(f"runtime attributes reference unknown tokens: {unknown}")
        unconfirmed = {
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.status != "confirmed"
        }
        if unconfirmed:
            raise ValueError(f"runtime attributes are not confirmed: {unconfirmed}")
        self.phases = {0: PhaseTracker(), 1: PhaseTracker()}

    @property
    def colors(self) -> dict[str, str]:
        return {token: style["color"] for token, style in self.token_styles.items()}

    def reset(self) -> None:
        for tracker in self.phases.values():
            tracker.reset()

    def order_tokens(self, tokens: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        return tuple(
            sorted(tokens, key=lambda token: self.token_styles.get(token, {}).get("order", 9999))
        )

    def classify(
        self, data: bytes, player: int, attack_judgment: bool = False
    ) -> SemanticResult:
        snapshot = EntitySnapshot.parse(data)
        if self.raw_states:
            return SemanticResult(self._raw_frame(snapshot))
        return SemanticResult(
            self._confirmed_frame(snapshot, player, attack_judgment)
        )

    def _runtime_tokens(self, snapshot: EntitySnapshot) -> tuple[str, ...]:
        return tuple(
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.display and attribute.matches(snapshot.raw)
        )

    def _confirmed_frame(
        self, snapshot: EntitySnapshot, player: int, attack_judgment: bool
    ) -> FrameBands:
        tracker = self.phases[player]
        if snapshot.actionable:
            tracker.reset()
            return FrameBands(False, action_frame=snapshot.action_frame, actionable=True)
        if not snapshot.action_type:
            tracker.reset()
            phase = "hard_lock"
        else:
            new_action = not tracker.active or snapshot.action_frame < tracker.last_frame
            if new_action:
                tracker.attack_seen = False
            tracker.attack_seen = tracker.attack_seen or attack_judgment
            tracker.active = True
            tracker.last_frame = snapshot.action_frame
            if attack_judgment:
                phase = "active"
            elif tracker.attack_seen:
                phase = "recovery"
            else:
                phase = "startup"
        tokens = [phase]
        if attack_judgment:
            tokens.append("attack")
        tokens.extend(self._runtime_tokens(snapshot))
        return FrameBands(
            relevant=True,
            action=phase,
            state=snapshot.state_code,
            action_frame=snapshot.action_frame,
            hitstop=snapshot.hitstop,
            codes=self.order_tokens(tokens),
            actionable=False,
        )

    @staticmethod
    def _raw_frame(snapshot: EntitySnapshot) -> FrameBands:
        if snapshot.actionable:
            return FrameBands(False, action_frame=snapshot.action_frame, actionable=True)
        codes: list[tuple[int, object]] = [(0, "locked")]
        if snapshot.state_code:
            codes.append((100 + snapshot.state_code, ("state", snapshot.state_code)))
        if snapshot.action_type:
            codes.append((200 + snapshot.action_type, ("action", snapshot.action_type)))
        if snapshot.control_state:
            codes.append((300 + snapshot.control_state, ("control", snapshot.control_state)))
        if snapshot.hitstop:
            codes.append((400, "hitstop"))
        codes.sort(key=lambda item: item[0])
        return FrameBands(
            relevant=True,
            action="locked",
            state=snapshot.state_code,
            action_frame=snapshot.action_frame,
            hitstop=snapshot.hitstop,
            codes=tuple(value for _order, value in codes),
            actionable=False,
        )
