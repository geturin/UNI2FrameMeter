from __future__ import annotations

import argparse
import colorsys
import ctypes
from ctypes import wintypes
import hashlib
from pathlib import Path
import struct
import tkinter as tk

from debug_capture import DebugCapture
from frame_timeline import EMPTY_FRAME, FrameBands, FrameTimeline
from semantic_engine import SemanticEngine
from uni2_frame_reader import (
    BATTLE_TICK_OFFSET,
    ENTITY_COUNT,
    ENTITY_POOL_OFFSET,
    ENTITY_STRIDE,
)
from uni2_probe import EXPECTED_SHA256, require_process


TRANSPARENT = "#010203"
GRID = "#313844"
EMPTY = "#080a0e"
LOCKED = "#cf3f83"
HITSTOP = "#f3c64d"
BUILD_ID = "2026-08-14-neutral-gap-timeline-v8"
ROOT = Path(__file__).resolve().parents[1]

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_NOACTIVATE = 0x08000000
SW_HIDE = 0
SW_SHOWNOACTIVATE = 4

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def stable_color(value: object, saturation: int = 62, lightness: int = 52) -> str:
    digest = hashlib.blake2s(repr(value).encode("utf-8"), digest_size=2).digest()
    hue = int.from_bytes(digest, "little") % 360
    red, green, blue = colorsys.hls_to_rgb(
        hue / 360.0, lightness / 100.0, saturation / 100.0
    )
    return f"#{round(red * 255):02x}{round(green * 255):02x}{round(blue * 255):02x}"


def game_window(pid: int) -> int | None:
    result: list[int] = []

    @WNDENUMPROC
    def callback(hwnd: int, _lparam: int) -> bool:
        window_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid and user32.IsWindowVisible(hwnd):
            if user32.GetWindowTextLengthW(hwnd) > 0:
                result.append(hwnd)
                return False
        return True

    user32.EnumWindows(callback, 0)
    return result[0] if result else None


def client_bounds(hwnd: int) -> tuple[int, int, int, int] | None:
    rect = RECT()
    origin = POINT(0, 0)
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        return None
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return origin.x, origin.y, width, height


def foreground_pid() -> int:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
    return int(pid.value)


def function_key_code(name: str) -> int:
    normalized = name.upper()
    if normalized.startswith("F") and normalized[1:].isdigit():
        number = int(normalized[1:])
        if 1 <= number <= 12:
            return 0x70 + number - 1
    raise ValueError("debug hotkey must be F1 through F12")


class Overlay:
    def __init__(
        self,
        duration: float | None = None,
        raw_states: bool = False,
        debug_hotkey: str = "F8",
        log_dir: Path = ROOT / "log",
    ):
        self.pid, self.process, self.module, digest = require_process()
        if digest != EXPECTED_SHA256:
            self.process.close()
            raise RuntimeError("uni2.exe SHA-256 does not match this overlay profile")
        self.game_hwnd = game_window(self.pid)
        if not self.game_hwnd:
            self.process.close()
            raise RuntimeError("unable to find the UNI2 game window")

        self.tick_address = self.module.base + BATTLE_TICK_OFFSET
        self.pool_address = self.module.base + ENTITY_POOL_OFFSET
        self.pool_size = ENTITY_STRIDE * ENTITY_COUNT
        self.previous_tick: int | None = None
        self.previous_actionable: tuple[bool, bool] | None = None
        self.timeline = FrameTimeline()
        self.semantic_engine = SemanticEngine(raw_states=raw_states)
        self.semantic_colors = self.semantic_engine.colors
        self.duration = duration
        self.raw_states = raw_states
        self.debug_hotkey = debug_hotkey.upper()
        self.debug_hotkey_code = function_key_code(debug_hotkey)
        self.debug_key_down = False
        self.debug_capture = DebugCapture(
            log_dir,
            ENTITY_POOL_OFFSET,
            self.pool_size,
            BATTLE_TICK_OFFSET,
            digest,
            BUILD_ID,
            "raw" if raw_states else "confirmed",
        )

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.configure(bg=TRANSPARENT)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.attributes("-alpha", 0.94)
        self.canvas = tk.Canvas(
            self.root, bg=TRANSPARENT, highlightthickness=0, borderwidth=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.update_idletasks()
        self.overlay_hwnd = int(self.root.winfo_id())
        parent = user32.GetParent(self.overlay_hwnd)
        if parent:
            self.overlay_hwnd = int(parent)
        style = user32.GetWindowLongW(self.overlay_hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(
            self.overlay_hwnd,
            GWL_EXSTYLE,
            style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE,
        )
        self.last_bounds: tuple[int, int, int, int] | None = None
        self.visible = False
        self.last_entities = (EMPTY_FRAME, EMPTY_FRAME)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        path = self.debug_capture.stop()
        if path is not None:
            print(f"[UNI2 overlay] debug recording stopped: {path.resolve()}", flush=True)
        self.process.close()
        self.root.destroy()

    def debug_pointer_preview(self, pointer: int, size: int = 0x60) -> dict[str, object] | None:
        if not pointer:
            return None
        raw = self.process.read(pointer, size)
        if raw is None:
            return {"pointer": pointer, "readable": False}
        text = raw.split(b"\0", 1)[0].decode("cp932", errors="replace")
        return {
            "pointer": pointer,
            "readable": True,
            "hash": hashlib.blake2s(raw, digest_size=8).hexdigest(),
            "head": raw.hex(),
            "text": text,
        }

    def sample(self) -> bool:
        raw_tick = self.process.read(self.tick_address, 4)
        if raw_tick is None:
            raise RuntimeError("battle tick became unreadable")
        tick = u32(raw_tick, 0)
        if tick == self.previous_tick:
            return False
        if self.previous_tick is not None and tick < self.previous_tick:
            self.timeline.reset()
            self.semantic_engine.reset()
        self.previous_tick = tick

        pool = self.process.read(self.pool_address, self.pool_size)
        if pool is None:
            raise RuntimeError("entity pool became unreadable")
        player_entities: dict[int, bytes] = {}
        attack_judgment = {0: False, 1: False}
        debug_entities: list[dict[str, object]] = []
        for slot in range(ENTITY_COUNT):
            start = slot * ENTITY_STRIDE
            entity = pool[start : start + ENTITY_STRIDE]
            if not u32(entity, 0x7BC):
                continue
            player = entity[0x438]
            if player in (0, 1):
                if player not in player_entities:
                    player_entities[player] = entity
                attack_judgment[player] = bool(
                    attack_judgment[player] or u32(entity, 0x64C)
                )
            state_label = entity[0xACC:0xB20].split(b"\0", 1)[0].decode(
                "ascii", errors="replace"
            )
            debug_entity: dict[str, object] = {
                    "slot": slot,
                    "player": player,
                    "character_id": entity[0x05],
                    "state": u32(entity, 0x24),
                    "movable": u32(entity, 0x440),
                    "action_type": u32(entity, 0x4B0),
                    "vulnerability_0060": u32(entity, 0x60),
                    "hit_filter_04a0": u32(entity, 0x4A0),
                    "descriptor": u32(entity, 0x644),
                    "animation_frame": u32(entity, 0x648),
                    "attack_data": u32(entity, 0x64C),
                    "action_frame": u32(entity, 0x674),
                    "flags_06b8": u32(entity, 0x6B8),
                    "flags_06c8": u32(entity, 0x6C8),
                    "action_record": u32(entity, 0x680),
                    "control_state": u32(entity, 0xB6C),
                    "hitstop": u32(entity, 0x1E4),
                    "label": state_label,
                }
            if self.debug_capture.active:
                debug_entity["references"] = {
                    "descriptor": self.debug_pointer_preview(u32(entity, 0x644)),
                    "animation": self.debug_pointer_preview(u32(entity, 0x648)),
                    "attack": self.debug_pointer_preview(u32(entity, 0x64C)),
                }
            debug_entities.append(debug_entity)
        players: dict[int, FrameBands] = {}
        for player, entity in player_entities.items():
            result = self.semantic_engine.classify(
                entity, player, attack_judgment[player]
            )
            players[player] = result.frame
        p1 = players.get(0, EMPTY_FRAME)
        p2 = players.get(1, EMPTY_FRAME)
        actionable = (p1.actionable, p2.actionable)
        if actionable != self.previous_actionable:
            labels = tuple("FREE" if value else "LOCK" for value in actionable)
            print(f"[UNI2 overlay] tick={tick} P1={labels[0]} P2={labels[1]}", flush=True)
            self.previous_actionable = actionable
        self.last_entities = (p1, p2)
        self.timeline.push(p1, p2)
        self.debug_capture.record(
            tick,
            pool,
            {
                "entities": debug_entities,
                "display": [
                    {
                        "actionable": frame.actionable,
                        "relevant": frame.relevant,
                        "codes": list(frame.codes),
                    }
                    for frame in (p1, p2)
                ],
                "players": [
                    {
                        "character_id": player_entities[player][0x05]
                        if player in player_entities
                        else None,
                        "raw_param1": (
                            (
                                u32(player_entities[player], 0x6B8)
                                | u32(player_entities[player], 0x6C8)
                            )
                            >> 16
                        )
                        if player in player_entities
                        else 0,
                    }
                    for player in (0, 1)
                ],
            },
        )
        return True

    def render(self, width: int, height: int) -> None:
        self.canvas.delete("all")
        if not self.timeline.frames:
            return
        bar_width = min(width - 24, 1120)
        grid_left = (width - bar_width) // 2
        grid_right = grid_left + bar_width
        gap = 4
        row_height = 52
        first_y = height - (row_height * 2 + gap + 12)
        cell_width = (grid_right - grid_left) / self.timeline.capacity
        frames = self.timeline.frames

        for player in range(2):
            y = first_y + player * (row_height + gap)
            for column in range(self.timeline.capacity):
                x0 = grid_left + column * cell_width
                x1 = grid_left + (column + 1) * cell_width - 1
                frame = frames[column][player] if column < len(frames) else EMPTY_FRAME
                self.canvas.create_rectangle(x0, y, x1, y + row_height, fill=EMPTY, outline="")
                # Free/actionable always wins over every secondary state.
                # The EMPTY rectangle drawn above remains untouched/black.
                if frame.relevant and not frame.actionable:
                    tokens = frame.codes or ("locked",)
                    lane_height = row_height / len(tokens)
                    for lane, token in enumerate(tokens):
                        y0 = y + lane * lane_height
                        color = (
                            self.semantic_colors[token]
                            if token in self.semantic_colors
                            else LOCKED
                            if token == "locked"
                            else HITSTOP
                            if token == "hitstop"
                            else stable_color(token)
                        )
                        self.canvas.create_rectangle(
                            x0,
                            y0,
                            x1,
                            y0 + lane_height,
                            fill=color,
                            outline="",
                        )
                self.canvas.create_rectangle(x0, y, x1, y + row_height, outline=GRID)

    def update(self) -> None:
        try:
            game_is_foreground = foreground_pid() == self.pid
            key_down = bool(
                game_is_foreground
                and user32.GetAsyncKeyState(self.debug_hotkey_code) & 0x8000
            )
            if key_down and not self.debug_key_down:
                path = self.debug_capture.toggle()
                if self.debug_capture.active:
                    print(
                        f"[UNI2 overlay] debug recording started: {path.resolve()}",
                        flush=True,
                    )
                elif path is not None:
                    print(
                        f"[UNI2 overlay] debug recording stopped: {path.resolve()}",
                        flush=True,
                    )
            self.debug_key_down = key_down
            changed = self.sample()
            bounds = client_bounds(self.game_hwnd)
            should_show = (
                bounds is not None
                and bounds[2] > 0
                and bounds[3] > 0
                and not user32.IsIconic(self.game_hwnd)
                and game_is_foreground
            )
            if should_show and bounds is not None:
                bounds_changed = bounds != self.last_bounds
                if bounds_changed:
                    self.root.geometry(f"{bounds[2]}x{bounds[3]}+{bounds[0]}+{bounds[1]}")
                    self.last_bounds = bounds
                if not self.visible:
                    user32.ShowWindow(self.overlay_hwnd, SW_SHOWNOACTIVATE)
                    self.visible = True
                if changed or bounds_changed:
                    self.render(bounds[2], bounds[3])
            elif self.visible:
                user32.ShowWindow(self.overlay_hwnd, SW_HIDE)
                self.visible = False
        except Exception:
            self.close()
            raise
        self.root.after(2, self.update)

    def run(self) -> None:
        self.update()
        if self.duration is not None:
            self.root.after(max(1, int(self.duration * 1000)), self.close)
        self.root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="External read-only UNI2 frame-meter overlay")
    parser.add_argument("--duration", type=float, help="optional automatic exit in seconds")
    parser.add_argument(
        "--raw-states",
        action="store_true",
        help="show the former all-raw-state diagnostic colors",
    )
    parser.add_argument(
        "--debug-hotkey",
        default="F8",
        help="F1-F12 key that toggles debug recording (default: F8)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=ROOT / "log",
        help="debug recording directory (default: ./log)",
    )
    args = parser.parse_args()
    print(
        f"[UNI2 overlay] build={BUILD_ID}; mode={'raw' if args.raw_states else 'confirmed'}; "
        f"debug={args.debug_hotkey.upper()}; actionable cells=black"
    )
    Overlay(
        args.duration,
        raw_states=args.raw_states,
        debug_hotkey=args.debug_hotkey,
        log_dir=args.log_dir,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
