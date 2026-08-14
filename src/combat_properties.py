from __future__ import annotations

from dataclasses import asdict, dataclass
import struct
from typing import Protocol


class MemoryReader(Protocol):
    def read(self, address: int, size: int) -> bytes | None: ...


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


@dataclass(frozen=True)
class CancelProperties:
    """Per-frame reconstruction of native BCMDTbl.CheckCancel (0x42B480).

    Nothing here reads the conditional result cache at entity+0x798..+0x79D.
    The persistent descriptor, timed overrides and impact flags are sampled
    every frame whether or not the game happened to call CheckCancel.
    """

    animation_pointer: int
    descriptor_pointer: int | None
    descriptor_normal_rule: int | None
    descriptor_special_rule: int | None
    descriptor_status1: int | None
    descriptor_actionable: int | None
    override_timer: int
    override_status: int
    impact_flags: int
    impact_result: int
    native_actionable: bool
    normal_rule: int
    special_rule: int
    normal: bool
    special: bool
    ex: bool
    chain_shift: bool
    read_error: str | None = None

    def tokens(self) -> tuple[str, ...]:
        return tuple(
            token
            for token, enabled in (
                ("normal_cancel", self.normal),
                ("special_cancel", self.special),
                ("ex_cancel", self.ex),
                ("cs_cancel", self.chain_shift),
            )
            if enabled
        )

    def debug_dict(self) -> dict[str, object]:
        return asdict(self)


def _cancel_rule_matches(rule: int, impact_result: int) -> bool:
    """Exact behavior of helper 0x42B3D0."""

    if rule == 1:  # _CancelFlag_Hit
        return bool(impact_result & 0x07)
    if rule == 2:  # _CancelFlag_Always
        return True
    if rule == 3:  # _CancelFlag_Damage
        return bool(impact_result & 0x02)
    return False


def read_cancel_properties(
    reader: MemoryReader, entity: bytes
) -> CancelProperties:
    animation_pointer = _u32(entity, 0x648)
    descriptor_pointer: int | None = None
    descriptor_normal_rule: int | None = None
    descriptor_special_rule: int | None = None
    descriptor_status1: int | None = None
    descriptor_actionable: int | None = None
    read_error: str | None = None

    if not animation_pointer:
        read_error = "null_animation_pointer"
    else:
        raw_pointer = reader.read(animation_pointer + 0x10C, 4)
        if raw_pointer is None or len(raw_pointer) != 4:
            read_error = "unreadable_descriptor_pointer"
        else:
            descriptor_pointer = _u32(raw_pointer, 0)
            if not descriptor_pointer:
                read_error = "null_descriptor_pointer"
            else:
                # One coherent read covers descriptor +0x0D through +0x1B.
                raw = reader.read(descriptor_pointer + 0x0D, 0x0F)
                if raw is None or len(raw) != 0x0F:
                    read_error = "unreadable_cancel_descriptor"
                else:
                    descriptor_normal_rule = raw[0x01]  # descriptor+0x0E
                    descriptor_special_rule = raw[0x02]  # descriptor+0x0F
                    descriptor_actionable = raw[0x04]  # descriptor+0x11
                    descriptor_status1 = _u32(raw, 0x0B)  # descriptor+0x18

    override_timer = _i32(entity, 0x46C)
    override_status = _u32(entity, 0x460)
    impact_flags = _u32(entity, 0x1CC)
    # CheckCancel converts +0x1CC to 0=no result, 1=contact, 2=damage.
    impact_result = 0 if impact_flags == 0 else (2 if impact_flags & 0x02 else 1)

    normal_rule = descriptor_normal_rule or 0
    special_rule = descriptor_special_rule or 0
    if override_timer > 0:
        normal_override = override_status & 0xFF
        special_override = (override_status >> 8) & 0xFF
        if normal_override != 0xFF:
            normal_rule = normal_override
        if special_override != 0xFF:
            special_rule = special_override

    # Exact freely-actionable shortcut at 0x424B80. A successful shortcut
    # makes native CheckCancel return 0xFF; timeline free cells remain black.
    native_actionable = False
    if descriptor_actionable is not None:
        if _i32(entity, 0x44C) > 0:
            native_actionable = entity[0x440] != 0
        elif _i32(entity, 0x45C) > 0:
            native_actionable = entity[0x450] != 0
        else:
            native_actionable = descriptor_actionable != 0

    dynamic_timer = _i32(entity, 0x48C)
    dynamic_flags = _u32(entity, 0x480) if dynamic_timer > 0 else 0
    status1 = descriptor_status1 or 0
    locked = not native_actionable and descriptor_pointer is not None
    return CancelProperties(
        animation_pointer=animation_pointer,
        descriptor_pointer=descriptor_pointer,
        descriptor_normal_rule=descriptor_normal_rule,
        descriptor_special_rule=descriptor_special_rule,
        descriptor_status1=descriptor_status1,
        descriptor_actionable=descriptor_actionable,
        override_timer=override_timer,
        override_status=override_status,
        impact_flags=impact_flags,
        impact_result=impact_result,
        native_actionable=native_actionable,
        normal_rule=normal_rule,
        special_rule=special_rule,
        normal=locked and _cancel_rule_matches(normal_rule, impact_result),
        special=locked and _cancel_rule_matches(special_rule, impact_result),
        ex=locked and bool((dynamic_flags & 0x01) or (status1 & 0x01)),
        chain_shift=locked and bool((dynamic_flags & 0x02) or (status1 & 0x08)),
        read_error=read_error,
    )


@dataclass(frozen=True)
class InvincibilityProperties:
    descriptor_pointer: int | None
    descriptor_invincibility: int | None
    hit_filter_timer: int
    hit_filter: int
    strike_timer: int
    throw_timer: int
    strike: bool
    body: bool
    throw: bool
    head: bool
    foot: bool
    light_foot: bool
    dive: bool
    projectile: bool
    full: bool
    read_error: str | None = None

    def tokens(self) -> tuple[str, ...]:
        return tuple(
            token
            for token, enabled in (
                ("strike_invincible", self.strike),
                ("body_invincible", self.body),
                ("throw_invincible", self.throw),
                ("head_invincible", self.head),
                ("foot_invincible", self.foot),
                ("light_foot_invincible", self.light_foot),
                ("dive_invincible", self.dive),
                ("projectile_invincible", self.projectile),
                ("full_invincible", self.full),
            )
            if enabled
        )

    def debug_dict(self) -> dict[str, object]:
        return asdict(self)


def read_invincibility_properties(
    reader: MemoryReader, entity: bytes
) -> InvincibilityProperties:
    """Read the inputs used by the native attribute rejection predicates.

    Current descriptor byte +0x0D is consumed by native strike/throw checks
    0x42DB70/0x42DB30. Values 3, 4 and 5 mean strike, throw and both/full.
    The per-attribute defender mask at entity+0x4A0 is valid only while its
    timed-state timer at +0x4AC is active (native 0x557170).
    """

    animation_pointer = _u32(entity, 0x648)
    descriptor_pointer: int | None = None
    descriptor_invincibility: int | None = None
    read_error: str | None = None
    if not animation_pointer:
        read_error = "null_animation_pointer"
    else:
        raw_pointer = reader.read(animation_pointer + 0x10C, 4)
        if raw_pointer is None or len(raw_pointer) != 4:
            read_error = "unreadable_descriptor_pointer"
        else:
            descriptor_pointer = _u32(raw_pointer, 0)
            if not descriptor_pointer:
                read_error = "null_descriptor_pointer"
            else:
                raw_value = reader.read(descriptor_pointer + 0x0D, 1)
                if raw_value is None or len(raw_value) != 1:
                    read_error = "unreadable_descriptor_invincibility"
                else:
                    descriptor_invincibility = raw_value[0]

    hit_filter_timer = _u32(entity, 0x4AC)
    hit_filter = _u32(entity, 0x4A0) if hit_filter_timer > 0 else 0
    strike_timer = max(entity[0x204], entity[0x206])
    throw_timer = max(entity[0x205], entity[0x207])
    descriptor_strike = descriptor_invincibility in (3, 5)
    descriptor_throw = descriptor_invincibility in (4, 5)
    strike = descriptor_strike or strike_timer > 0
    throw = descriptor_throw or throw_timer > 0 or bool(hit_filter & 0x10)
    return InvincibilityProperties(
        descriptor_pointer=descriptor_pointer,
        descriptor_invincibility=descriptor_invincibility,
        hit_filter_timer=hit_filter_timer,
        hit_filter=hit_filter,
        strike_timer=strike_timer,
        throw_timer=throw_timer,
        strike=strike,
        body=bool(hit_filter & 0x02),
        throw=throw,
        head=bool(hit_filter & 0x01),
        foot=bool(hit_filter & 0x04),
        light_foot=bool(hit_filter & 0x100),
        dive=bool(hit_filter & 0x40),
        projectile=bool(hit_filter & 0x08),
        full=(descriptor_invincibility == 5 or (strike and throw)),
        read_error=read_error,
    )
