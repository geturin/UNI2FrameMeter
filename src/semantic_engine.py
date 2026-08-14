from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import struct
import sys
from typing import Any

from frame_timeline import FrameBands


def runtime_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


DEFAULT_PROFILE = runtime_directory() / "frame_semantics.json"

# Battle_Std itself uses this exact union when it needs to ask whether the
# current move is an attack, a skill or a throw.  These are MoveCode bank 0
# bits at entity+0x6AC, not the timed HitCheck structures at +0x4A0/+0x4B0.
MOVE_CODE_ATTACK = 0x01
MOVE_CODE_SKILL = 0x02
MOVE_CODE_THROW = 0x04
ATTACK_MOVE_CODE_MASK = MOVE_CODE_ATTACK | MOVE_CODE_SKILL | MOVE_CODE_THROW


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def is_actionable(movable: int, state_label: bytes = b"") -> bool:
    return movable != 0 or state_label.startswith(b"Mv_Modori_Guard")


def is_control_locked(movable: int, state_label: bytes = b"") -> bool:
    return not is_actionable(movable, state_label)


@dataclass(frozen=True)
class EntitySnapshot:
    raw: bytes
    state_code: int
    movable: int
    move_code: int
    action_instance: int
    landing_lock: int
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
            move_code=u32(data, 0x6AC),
            action_instance=u32(data, 0x680),
            landing_lock=u32(data, 0x44C),
            action_frame=u32(data, 0x674),
            hitstop=u32(data, 0x1E4),
            control_state=u32(data, 0xB6C),
            state_label=data[0xACC:0xB20].split(b"\0", 1)[0],
        )

    @property
    def actionable(self) -> bool:
        if is_actionable(self.movable, self.state_label):
            return True
        # During the generic landing transition (+0xB6C == 2), +0x44C
        # counts forced recovery down to zero. The remaining presentation is
        # guard-cancellable even though ordinary movement stays disabled.
        return (
            not self.attack_action
            and self.control_state == 2
            and self.landing_lock == 0
        )

    @property
    def attack_action(self) -> bool:
        return bool(self.move_code & ATTACK_MOVE_CODE_MASK)


@dataclass(frozen=True)
class RuntimeCondition:
    offset: int
    mask: int
    equals: int | None = None
    not_equals: int | None = None

    def matches(self, data: bytes) -> bool:
        value = u32(data, self.offset) & self.mask
        if self.equals is not None and value != self.equals:
            return False
        if self.not_equals is not None and value == self.not_equals:
            return False
        return True


@dataclass(frozen=True)
class RuntimeAttribute:
    token: str
    display: bool
    status: str
    condition_groups: tuple[tuple[RuntimeCondition, ...], ...]

    def matches(self, data: bytes) -> bool:
        return any(
            all(condition.matches(data) for condition in group)
            for group in self.condition_groups
        )


@dataclass(frozen=True)
class SemanticResult:
    frame: FrameBands


@dataclass
class PhaseTracker:
    active: bool = False
    last_frame: int = 0
    attack_seen: bool = False
    last_action_instance: int = 0

    def reset(self) -> None:
        self.active = False
        self.last_frame = 0
        self.attack_seen = False
        self.last_action_instance = 0


class SemanticEngine:
    """Convert each live entity snapshot directly into one display cell."""

    def __init__(self, profile: Path = DEFAULT_PROFILE, raw_states: bool = False):
        document = json.loads(profile.read_text(encoding="utf-8"))
        if document.get("schema_version") != 2:
            raise ValueError("unsupported frame-semantics profile schema")
        self.raw_states = raw_states
        self.token_styles: dict[str, dict[str, Any]] = document["tokens"]
        def parse_condition(condition: dict[str, Any]) -> RuntimeCondition:
            return RuntimeCondition(
                offset=int(condition["offset"], 0),
                mask=int(condition["mask"], 0),
                equals=(
                    int(condition["equals"], 0)
                    if "equals" in condition
                    else None
                ),
                not_equals=(
                    int(condition["not_equals"], 0)
                    if "not_equals" in condition
                    else None
                ),
            )

        def parse_groups(attribute: dict[str, Any]) -> tuple[tuple[RuntimeCondition, ...], ...]:
            raw_groups = attribute.get("condition_groups")
            if raw_groups is None:
                raw_groups = [attribute.get("conditions", [attribute])]
            return tuple(
                tuple(parse_condition(condition) for condition in group)
                for group in raw_groups
            )

        self.runtime_attributes = tuple(
            RuntimeAttribute(
                token=attribute["token"],
                display=bool(attribute["display"]),
                status=str(attribute["status"]),
                condition_groups=parse_groups(attribute),
            )
            for attribute in document["runtime_attributes"]
        )
        external_definitions = document.get("external_attributes", [])
        self.external_attributes = {
            attribute["token"]: bool(attribute["display"])
            for attribute in external_definitions
        }
        self.attribute_status = {
            attribute["token"]: str(attribute["status"])
            for attribute in external_definitions
        }
        self.attribute_status.update(
            {
                attribute.token: attribute.status
                for attribute in self.runtime_attributes
            }
        )
        unknown = {
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.token not in self.token_styles
        }
        unknown.update(
            token
            for token in self.external_attributes
            if token not in self.token_styles
        )
        if unknown:
            raise ValueError(f"runtime attributes reference unknown tokens: {unknown}")
        unconfirmed = {
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.display and attribute.status != "confirmed"
        }
        unconfirmed.update(
            attribute["token"]
            for attribute in external_definitions
            if bool(attribute["display"]) and attribute["status"] != "confirmed"
        )
        if unconfirmed:
            raise ValueError(f"runtime attributes are not confirmed: {unconfirmed}")
        self.phases = {0: PhaseTracker(), 1: PhaseTracker()}

    @property
    def colors(self) -> dict[str, str]:
        return {token: style["color"] for token, style in self.token_styles.items()}

    def reset(self) -> None:
        for tracker in self.phases.values():
            tracker.reset()

    def set_attribute_display(self, token: str, display: bool) -> None:
        if token not in self.attribute_status:
            raise KeyError(token)
        if display and self.attribute_status[token] != "confirmed":
            raise ValueError(f"cannot display unconfirmed attribute: {token}")
        if token in self.external_attributes:
            self.external_attributes[token] = bool(display)
        self.runtime_attributes = tuple(
            replace(attribute, display=bool(display))
            if attribute.token == token
            else attribute
            for attribute in self.runtime_attributes
        )

    def order_tokens(self, tokens: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        return tuple(
            sorted(tokens, key=lambda token: self.token_styles.get(token, {}).get("order", 9999))
        )

    def classify(
        self,
        data: bytes,
        player: int,
        attack_judgment: bool = False,
        external_tokens: tuple[str, ...] = (),
        world_tokens: tuple[str, ...] = (),
    ) -> SemanticResult:
        snapshot = EntitySnapshot.parse(data)
        if self.raw_states:
            frame = self._raw_frame(snapshot)
        else:
            frame = self._confirmed_frame(
                snapshot, player, attack_judgment, external_tokens
            )
        displayed_world_tokens = tuple(
            token
            for token in world_tokens
            if self.external_attributes.get(token, False)
        )
        if displayed_world_tokens:
            frame = replace(
                frame,
                relevant=True,
                codes=self.order_tokens(frame.codes + displayed_world_tokens),
            )
        return SemanticResult(frame)

    def _runtime_tokens(self, snapshot: EntitySnapshot) -> tuple[str, ...]:
        return tuple(
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.display and attribute.matches(snapshot.raw)
        )

    def _confirmed_frame(
        self,
        snapshot: EntitySnapshot,
        player: int,
        attack_judgment: bool,
        external_tokens: tuple[str, ...],
    ) -> FrameBands:
        tracker = self.phases[player]
        if snapshot.actionable:
            tracker.reset()
            return FrameBands(False, action_frame=snapshot.action_frame, actionable=True)
        if not snapshot.attack_action:
            tracker.reset()
            phase = "control_lock"
        else:
            new_action = (
                not tracker.active
                or snapshot.action_frame < tracker.last_frame
                or snapshot.action_instance != tracker.last_action_instance
            )
            if new_action:
                tracker.attack_seen = False
            tracker.attack_seen = tracker.attack_seen or attack_judgment
            tracker.active = True
            tracker.last_frame = snapshot.action_frame
            tracker.last_action_instance = snapshot.action_instance
            if attack_judgment:
                phase = "active"
            elif tracker.attack_seen:
                phase = "recovery"
            else:
                phase = "startup"
        # The internal active phase and the confirmed attack judgment describe
        # the same frames in every validated capture. Keep the phase for
        # startup/recovery tracking, but render only the attack token so those
        # frames do not occupy two identical semantic bands.
        tokens = [] if phase == "active" else [phase]
        if attack_judgment:
            tokens.append("attack")
        tokens.extend(self._runtime_tokens(snapshot))
        tokens.extend(
            token
            for token in external_tokens
            if self.external_attributes.get(token, False)
        )
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
        if snapshot.move_code:
            codes.append((200, ("move_code", snapshot.move_code)))
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
