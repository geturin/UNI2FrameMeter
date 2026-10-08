from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import struct
import sys
from typing import Any

from semantic_profile import load_profile
from combat_states import BoundState

from frame_timeline import FrameBands
from runtime_layout import (
    MOVE_CODE_OFFSET, ACTION_FRAME_OFFSET, ACTION_INSTANCE_OFFSET,
    MOVABLE_OFFSET, LANDING_LOCK_OFFSET, HITSTOP_OFFSET, LABEL_OFFSET, LABEL_BYTES,
)


def runtime_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


DEFAULT_PROFILE = runtime_directory() / "frame_semantics.json"

# These are the game's named MoveCode bank 0 flags at entity+0x6B8.
# The meter treats Attack, Skill and Throw as attack actions for phase
# tracking. FireBall (0x04) is a different flag, not Throw (0x20).
# Neither bank is the timed HitCheck structure at +0x49C/+0x4AC.
MOVE_CODE_ATTACK = 0x01
MOVE_CODE_SKILL = 0x02
MOVE_CODE_THROW = 0x20
ATTACK_MOVE_CODE_MASK = MOVE_CODE_ATTACK | MOVE_CODE_SKILL | MOVE_CODE_THROW


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


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
    control_state: int | None
    state_label: bytes
    native_actionable: bool | None = None

    @classmethod
    def parse(cls, data: bytes, native_actionable: bool | None = None) -> "EntitySnapshot":
        return cls(
            raw=data,
            # Historical field name retained internally. +0x24 is a WORD
            # DataDelay diagnostic, not a character-state enumeration.
            state_code=struct.unpack_from("<H", data, 0x24)[0],
            movable=data[MOVABLE_OFFSET],
            move_code=u32(data, MOVE_CODE_OFFSET),
            action_instance=u32(data, ACTION_INSTANCE_OFFSET),
            landing_lock=struct.unpack_from("<i", data, LANDING_LOCK_OFFSET)[0],
            action_frame=u32(data, ACTION_FRAME_OFFSET),
            hitstop=struct.unpack_from("<h", data, HITSTOP_OFFSET)[0],
            control_state=None,
            state_label=data[LABEL_OFFSET:LABEL_OFFSET + LABEL_BYTES].split(b"\0", 1)[0],
            native_actionable=native_actionable,
        )

    @property
    def actionable(self) -> bool:
        if self.native_actionable is not None:
            return self.native_actionable
        raise RuntimeError("The native action-permission predicate was not supplied for this snapshot")

    @property
    def attack_action(self) -> bool:
        return bool(self.move_code & ATTACK_MOVE_CODE_MASK)


@dataclass(frozen=True)
class RuntimeCondition:
    offset: int
    mask: int
    equals: int | None = None
    not_equals: int | None = None
    size: int = 4
    signed: bool = False
    greater_than: int | None = None

    def __post_init__(self) -> None:
        if self.size not in (1, 2, 4) or self.offset < 0:
            raise ValueError("runtime condition has an invalid field layout")
        if not 0 <= self.mask < (1 << (self.size * 8)):
            raise ValueError("runtime condition mask exceeds its field width")
        if self.signed and self.mask != (1 << (self.size * 8)) - 1:
            raise ValueError("signed runtime conditions require a full-width mask")

    def matches(self, data: bytes) -> bool:
        if self.offset + self.size > len(data):
            raise ValueError("runtime condition is outside the native snapshot")
        value = int.from_bytes(data[self.offset:self.offset + self.size], "little") & self.mask
        if self.signed and value & (1 << (self.size * 8 - 1)):
            value -= 1 << (self.size * 8)
        if self.equals is not None and value != self.equals:
            return False
        if self.not_equals is not None and value == self.not_equals:
            return False
        if self.greater_than is not None and value <= self.greater_than:
            return False
        return True


@dataclass(frozen=True)
class RuntimeAttribute:
    token: str
    display: bool
    status: str
    condition_groups: tuple[tuple[RuntimeCondition, ...], ...]
    scope: str = "action"

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
        document = load_profile(profile)
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
                size=int(condition.get("size", 4)),
                signed=bool(condition.get("signed", False)),
                greater_than=(
                    int(condition["greater_than"], 0)
                    if "greater_than" in condition
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
                scope=str(attribute.get("scope", "action")),
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
        status_tokens: tuple[str, ...] = (),
        native_actionable: bool | None = None,
    ) -> SemanticResult:
        snapshot = EntitySnapshot.parse(data, native_actionable=native_actionable)
        if self.raw_states:
            frame = self._raw_frame(snapshot)
        else:
            frame = self._confirmed_frame(
                snapshot, player, attack_judgment, external_tokens
            )
        # Buffs such as two-way guard remain meaningful while the recipient
        # can act. Keep them separate from action-bound cancel/invincibility
        # attributes, which the confirmed frame deliberately hides when free.
        displayed_independent_tokens = tuple(
            token
            for token in world_tokens + status_tokens
            if self.external_attributes.get(token, False)
        ) + self._runtime_tokens(snapshot, independent=True)
        if displayed_independent_tokens:
            frame = replace(
                frame,
                relevant=True,
                codes=self.order_tokens(frame.codes + displayed_independent_tokens),
            )
        return SemanticResult(frame)

    def _runtime_tokens(self, snapshot: EntitySnapshot, independent: bool = False) -> tuple[str, ...]:
        return tuple(
            attribute.token
            for attribute in self.runtime_attributes
            if attribute.display and (attribute.scope == "independent") == independent
            and attribute.matches(snapshot.raw)
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
        state_token = BoundState.parse(snapshot.raw).token
        if state_token is not None or not snapshot.attack_action:
            tracker.reset()
            phase = (
                state_token
                if state_token is not None and self.external_attributes.get(state_token, False)
                else "control_lock"
            )
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
        # During an attack action, draw its active phase once using the attack
        # token. A native bound-state band may coexist with a current attack
        # record; the record alone does not prove a hit or collision result.
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
            codes.append((100 + snapshot.state_code, ("data_delay", snapshot.state_code)))
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
