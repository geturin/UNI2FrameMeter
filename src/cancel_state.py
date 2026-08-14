from __future__ import annotations

from dataclasses import asdict, dataclass
import struct
from typing import Protocol


class MemoryReader(Protocol):
    def read(self, address: int, size: int) -> bytes | None: ...


def _u32(data: bytes, offset: int = 0) -> int:
    return struct.unpack_from("<I", data, offset)[0]


@dataclass(frozen=True)
class ChainShiftState:
    """Inputs used by native BCMDTbl.CheckCancel(_SkillType_ChainShift)."""

    dynamic_timer: int
    dynamic_flags: int
    dynamic_allowed: bool
    animation_pointer: int
    descriptor_pointer: int | None
    descriptor_flags: int | None
    descriptor_allowed: bool
    allowed: bool
    read_error: str | None = None

    def debug_dict(self) -> dict[str, object]:
        return asdict(self)


def read_chain_shift_state(reader: MemoryReader, entity: bytes) -> ChainShiftState:
    """Reproduce the non-free branch of native function 0x42B480.

    The caller handles the game's freely-actionable shortcut.  This routine
    deliberately reads the game's natural cancel descriptor and never writes
    to the process.
    """

    dynamic_flags = _u32(entity, 0x480)
    dynamic_timer = _u32(entity, 0x48C)
    dynamic_allowed = dynamic_timer > 0 and bool(dynamic_flags & 0x2)
    animation_pointer = _u32(entity, 0x648)

    descriptor_pointer: int | None = None
    descriptor_flags: int | None = None
    read_error: str | None = None
    if not animation_pointer:
        read_error = "null_animation_pointer"
    else:
        raw_pointer = reader.read(animation_pointer + 0x10C, 4)
        if raw_pointer is None or len(raw_pointer) != 4:
            read_error = "unreadable_descriptor_pointer"
        else:
            descriptor_pointer = _u32(raw_pointer)
            if not descriptor_pointer:
                read_error = "null_descriptor_pointer"
            else:
                raw_flags = reader.read(descriptor_pointer + 0x18, 1)
                if raw_flags is None or len(raw_flags) != 1:
                    read_error = "unreadable_descriptor_flags"
                else:
                    descriptor_flags = raw_flags[0]

    descriptor_allowed = bool(
        descriptor_flags is not None and descriptor_flags & 0x08
    )
    return ChainShiftState(
        dynamic_timer=dynamic_timer,
        dynamic_flags=dynamic_flags,
        dynamic_allowed=dynamic_allowed,
        animation_pointer=animation_pointer,
        descriptor_pointer=descriptor_pointer,
        descriptor_flags=descriptor_flags,
        descriptor_allowed=descriptor_allowed,
        allowed=dynamic_allowed or descriptor_allowed,
        read_error=read_error,
    )
