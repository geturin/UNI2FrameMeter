from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable


@dataclass(frozen=True)
class FrameBands:
    relevant: bool
    action: Hashable | None = None
    state: Hashable | None = None
    flags: Hashable | None = None
    descriptor: Hashable | None = None
    action_frame: int = 0
    hitstop: int = 0
    codes: tuple[Hashable, ...] = ()
    # Authoritative action-permission result. When true the cell must remain
    # black even if animation/state fields still contain non-zero values.
    actionable: bool = False


EMPTY_FRAME = FrameBands(False, actionable=True)


@dataclass
class FrameTimeline:
    capacity: int = 60
    idle_reset_frames: int = 60
    frames: list[tuple[FrameBands, FrameBands]] = field(default_factory=list)
    running: bool = False
    idle_frames: int = 0

    def reset(self) -> None:
        self.frames.clear()
        self.running = False
        self.idle_frames = 0

    def push(self, p1: FrameBands, p2: FrameBands) -> None:
        active = p1.relevant or p2.relevant
        if active:
            if not self.running and self.idle_frames >= self.idle_reset_frames:
                self.frames.clear()
            elif not self.running and self.idle_frames:
                # The display stays visually frozen while both players are
                # free, but elapsed logic frames still occupy time. Materialize
                # that interval as black cells when activity resumes.
                for _ in range(self.idle_frames):
                    self._append(EMPTY_FRAME, EMPTY_FRAME)
            self.running = True
            self.idle_frames = 0
            self._append(p1, p2)
            return

        if not self.frames:
            return

        # Preserve the completed result while both players can act. Neutral
        # logic frames are counted only to decide whether the next action is a
        # new session; they never scroll the visible meter.
        self.idle_frames += 1
        self.running = False

    def _append(self, p1: FrameBands, p2: FrameBands) -> None:
        self.frames.append((p1, p2))
        if len(self.frames) > self.capacity:
            del self.frames[: len(self.frames) - self.capacity]
