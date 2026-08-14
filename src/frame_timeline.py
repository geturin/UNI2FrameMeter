from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
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
    # Authoritative action-permission result. Ordinary character-local states
    # remain black while true, but an independently active world object such
    # as a projectile may still make the frame relevant and add a color band.
    actionable: bool = False


EMPTY_FRAME = FrameBands(False, actionable=True)


@dataclass(frozen=True)
class TimelineSettings:
    length_frames: int = 120
    idle_reset_frames: int = 60
    wrap_gap_frames: int = 5
    max_width_pixels: int = 1440
    current_frame_border_color: str = "#ffffff"
    show_primary_run_counts: bool = True
    primary_run_count_color: str = "#ffffff"
    primary_run_count_font_size: int = 9

    @classmethod
    def load(cls, profile: Path) -> "TimelineSettings":
        document = json.loads(profile.read_text(encoding="utf-8"))
        values = document.get("timeline", {})
        settings = cls(
            length_frames=int(values.get("length_frames", cls.length_frames)),
            idle_reset_frames=int(
                values.get("idle_reset_frames", cls.idle_reset_frames)
            ),
            wrap_gap_frames=int(
                values.get("wrap_gap_frames", cls.wrap_gap_frames)
            ),
            max_width_pixels=int(
                values.get("max_width_pixels", cls.max_width_pixels)
            ),
            current_frame_border_color=str(
                values.get(
                    "current_frame_border_color",
                    cls.current_frame_border_color,
                )
            ),
            show_primary_run_counts=bool(
                values.get(
                    "show_primary_run_counts",
                    cls.show_primary_run_counts,
                )
            ),
            primary_run_count_color=str(
                values.get(
                    "primary_run_count_color",
                    cls.primary_run_count_color,
                )
            ),
            primary_run_count_font_size=int(
                values.get(
                    "primary_run_count_font_size",
                    cls.primary_run_count_font_size,
                )
            ),
        )
        if settings.length_frames < 2:
            raise ValueError("timeline.length_frames must be at least 2")
        if settings.idle_reset_frames < 1:
            raise ValueError("timeline.idle_reset_frames must be at least 1")
        if not 0 <= settings.wrap_gap_frames < settings.length_frames:
            raise ValueError(
                "timeline.wrap_gap_frames must be between 0 and length_frames - 1"
            )
        if settings.max_width_pixels < settings.length_frames:
            raise ValueError(
                "timeline.max_width_pixels must be at least timeline.length_frames"
            )
        if not (
            len(settings.current_frame_border_color) == 7
            and settings.current_frame_border_color.startswith("#")
        ):
            raise ValueError(
                "timeline.current_frame_border_color must be a #RRGGBB color"
            )
        if not (
            len(settings.primary_run_count_color) == 7
            and settings.primary_run_count_color.startswith("#")
        ):
            raise ValueError(
                "timeline.primary_run_count_color must be a #RRGGBB color"
            )
        if settings.primary_run_count_font_size < 1:
            raise ValueError(
                "timeline.primary_run_count_font_size must be positive"
            )
        return settings


@dataclass(frozen=True)
class PrimaryBandRun:
    player: int
    first_column: int
    last_column: int
    token: Hashable

    @property
    def frames(self) -> int:
        return self.last_column - self.first_column + 1


def primary_band_runs(
    frames: list[tuple[FrameBands, FrameBands]], player: int
) -> list[PrimaryBandRun]:
    """Find physical, visible runs of the first color band for one player."""
    runs: list[PrimaryBandRun] = []
    current_token: Hashable | None = None
    first_column = 0
    for column, pair in enumerate(frames):
        frame = pair[player]
        token = frame.codes[0] if frame.relevant and frame.codes else None
        if token == current_token:
            continue
        if current_token is not None:
            runs.append(
                PrimaryBandRun(
                    player,
                    first_column,
                    column - 1,
                    current_token,
                )
            )
        current_token = token
        first_column = column
    if current_token is not None:
        runs.append(
            PrimaryBandRun(
                player,
                first_column,
                len(frames) - 1,
                current_token,
            )
        )
    return runs


@dataclass
class FrameTimeline:
    capacity: int = 120
    idle_reset_frames: int = 60
    tail_gap: int = 5
    frames: list[tuple[FrameBands, FrameBands]] = field(default_factory=list)
    running: bool = False
    idle_frames: int = 0
    write_index: int = 0
    written_frames: int = 0

    @property
    def last_written_index(self) -> int | None:
        if not self.frames or not self.written_frames:
            return None
        return (self.write_index - 1) % self.capacity

    def reset(self) -> None:
        self.frames.clear()
        self.running = False
        self.idle_frames = 0
        self.write_index = 0
        self.written_frames = 0

    def push(self, p1: FrameBands, p2: FrameBands) -> None:
        active = p1.relevant or p2.relevant
        if active:
            if not self.running and self.idle_frames >= self.idle_reset_frames:
                self.reset()
            elif not self.running and self.idle_frames:
                # The display stays visually frozen while both players are
                # free, but elapsed logic frames still occupy time. Materialize
                # that interval as black cells when activity resumes.
                for _ in range(self.idle_frames):
                    self._write(EMPTY_FRAME, EMPTY_FRAME)
            self.running = True
            self.idle_frames = 0
            self._write(p1, p2)
            return

        if not self.frames:
            return

        # Preserve the completed result while both players can act. Neutral
        # logic frames are counted only to decide whether the next action is a
        # new session; they never scroll the visible meter.
        self.idle_frames += 1
        self.running = False

    def _write(self, p1: FrameBands, p2: FrameBands) -> None:
        """Write exact frames into fixed slots with a right-moving cursor."""
        if not self.frames:
            self.frames = [
                (EMPTY_FRAME, EMPTY_FRAME) for _ in range(self.capacity)
            ]

        current = self.write_index
        self.frames[current] = (p1, p2)

        # StriveFrameViewer clears a slot five positions ahead of its circular
        # cursor. In steady state this produces five black cells separating the
        # newest left-to-right pass from older cells that have not yet been
        # overwritten. Unlike that project, we keep every logic frame exact
        # and rely on the larger 120-slot bar instead of segment compression.
        if self.tail_gap:
            clear_index = (
                current + min(self.tail_gap, self.capacity - 1)
            ) % self.capacity
            self.frames[clear_index] = (EMPTY_FRAME, EMPTY_FRAME)

        self.write_index = (current + 1) % self.capacity
        self.written_frames += 1

    def chronological_frames(self) -> list[tuple[FrameBands, FrameBands]]:
        """Return recorded slots in time order for diagnostics and tests."""
        if not self.frames:
            return []
        count = min(self.written_frames, self.capacity)
        if self.written_frames < self.capacity:
            return self.frames[:count]
        return [
            self.frames[(self.write_index + offset) % self.capacity]
            for offset in range(count)
        ]
