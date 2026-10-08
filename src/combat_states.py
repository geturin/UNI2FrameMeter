"""Character state categories read from the game's native BoundStatus fields.

This module does not execute or reconstruct combat. Offsets below match
BtlMvStd.GetBoundStatus (0x89AB60) in the supported executable. Capture is
tested first: a captured character can retain bound/guard fields as well.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct

from runtime_layout import (
    CAPTURE_OFFSET, BOUND_OFFSET, BOUND_GUARD_OFFSET, BOUND_DOWN_OFFSET,
)


@dataclass(frozen=True)
class BoundState:
    captured: bool
    bound: bool
    guarding: bool
    down: bool

    @classmethod
    def parse(cls, entity: bytes) -> "BoundState":
        bound = struct.unpack_from("<I", entity, BOUND_OFFSET)[0] != 0
        return cls(
            captured=entity[CAPTURE_OFFSET] != 0,
            bound=bound,
            guarding=bound and entity[BOUND_GUARD_OFFSET] != 0,
            down=bound and struct.unpack_from("<h", entity, BOUND_DOWN_OFFSET)[0] != 0,
        )

    @property
    def token(self) -> str | None:
        if self.captured:
            return "capture"
        if self.down:
            return "knockdown"
        if self.guarding:
            return "guardstun"
        if self.bound:
            return "hitstun"
        return None
