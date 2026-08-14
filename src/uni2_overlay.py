from __future__ import annotations

import argparse
import colorsys
import ctypes
from ctypes import wintypes
import hashlib
from pathlib import Path
import struct
import threading
import time
import tkinter as tk
from tkinter import ttk

from combat_properties import (
    CancelProperties,
    InvincibilityProperties,
    read_cancel_properties,
    read_invincibility_properties,
)
from battle_objects import (
    projectile_judgment_by_owner,
    read_battle_objects,
)
from debug_capture import DebugCapture
from display_config import DisplayConfig
from frame_timeline import (
    EMPTY_FRAME,
    FrameBands,
    FrameTimeline,
    TimelineSettings,
    primary_band_runs,
)
from semantic_engine import DEFAULT_PROFILE, SemanticEngine
from runtime_layout import (
    ENTITY_COUNT,
    ENTITY_STRIDE,
    resolve_runtime_layout,
    validate_runtime_layout,
)
from process_memory import require_process


TRANSPARENT = "#010203"
GRID = "#313844"
EMPTY = "#080a0e"
LOCKED = "#cf3f83"
HITSTOP = "#f3c64d"
BUILD_ID = "v0.5-dedicated-tick-sampler"
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
winmm = ctypes.WinDLL("winmm", use_last_error=True)
winmm.timeBeginPeriod.argtypes = [wintypes.UINT]
winmm.timeBeginPeriod.restype = wintypes.UINT
winmm.timeEndPeriod.argtypes = [wintypes.UINT]
winmm.timeEndPeriod.restype = wintypes.UINT


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
        profile: Path = DEFAULT_PROFILE,
    ):
        self.pid, self.process, self.module, digest = require_process()
        try:
            self.layout = resolve_runtime_layout(Path(self.process.image_path()))
            validate_runtime_layout(self.process, self.module.base, self.layout)
        except Exception:
            self.process.close()
            raise
        print(
            "[UNI2 overlay] runtime layout: "
            f"tick=+0x{self.layout.battle_tick_offset:X} "
            f"entities=+0x{self.layout.entity_pool_offset:X} "
            f"objects=+0x{self.layout.object_count_offset:X}/"
            f"+0x{self.layout.object_pointers_offset:X}",
            flush=True,
        )
        self.game_hwnd = game_window(self.pid)
        if not self.game_hwnd:
            self.process.close()
            raise RuntimeError("unable to find the UNI2 game window")

        self.tick_address = self.module.base + self.layout.battle_tick_offset
        self.pool_address = self.module.base + self.layout.entity_pool_offset
        self.pool_size = ENTITY_STRIDE * ENTITY_COUNT
        self.previous_tick: int | None = None
        self.previous_actionable: tuple[bool, bool] | None = None
        self.profile = profile.resolve()
        self.display_config = DisplayConfig.load(self.profile)
        self.timeline_settings = TimelineSettings.load(profile)
        self.timeline = FrameTimeline(
            capacity=self.timeline_settings.length_frames,
            idle_reset_frames=self.timeline_settings.idle_reset_frames,
            tail_gap=self.timeline_settings.wrap_gap_frames,
        )
        self.semantic_engine = SemanticEngine(profile=profile, raw_states=raw_states)
        self.semantic_colors = self.semantic_engine.colors
        self.duration = duration
        self.raw_states = raw_states
        self.debug_hotkey = debug_hotkey.upper()
        self.debug_hotkey_code = function_key_code(debug_hotkey)
        self.debug_key_down = False
        self.debug_capture = DebugCapture(
            log_dir,
            self.layout.entity_pool_offset,
            self.pool_size,
            self.layout.battle_tick_offset,
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
        self.projectile_judgment = (False, False)
        self.closed = False
        self.timer_resolution_active = False
        self.state_lock = threading.RLock()
        self.stop_sampling = threading.Event()
        self.sampling_thread: threading.Thread | None = None
        self.sampling_error: BaseException | None = None
        self.sample_generation = 0
        self.rendered_generation = 0
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.create_control_window()

    def create_control_window(self) -> None:
        self.control_window = tk.Toplevel(self.root)
        self.control_window.title("UNI2 Frame Display")
        self.control_window.resizable(False, False)
        self.control_window.attributes("-topmost", True)
        self.control_window.protocol("WM_DELETE_WINDOW", self.close)
        container = ttk.Frame(self.control_window, padding=8)
        container.grid(row=0, column=0, sticky="nsew")
        self.display_variables: dict[str, tk.BooleanVar] = {}
        for row, item in enumerate(self.display_config.items()):
            variable = tk.BooleanVar(value=item.display)
            self.display_variables[item.token] = variable
            checkbox = ttk.Checkbutton(
                container,
                text=item.token,
                variable=variable,
                command=lambda token=item.token: self.toggle_display(token),
            )
            if item.status != "confirmed":
                checkbox.state(["disabled"])
            checkbox.grid(row=row, column=0, sticky="w", pady=1)
        self.control_window.update_idletasks()
        self.control_window.geometry("+20+20")

    def toggle_display(self, token: str) -> None:
        variable = self.display_variables[token]
        display = bool(variable.get())
        try:
            with self.state_lock:
                self.display_config.set_display(token, display)
                self.semantic_engine.set_attribute_display(token, display)
                # Existing cells were classified under the former visibility
                # set. Clear them so the checkbox is effective immediately.
                self.timeline.reset()
                self.semantic_engine.reset()
                self.previous_actionable = None
                self.sample_generation += 1
        except (OSError, ValueError, KeyError) as error:
            variable.set(not display)
            print(f"[UNI2 overlay] unable to update {token}: {error}", flush=True)
            return

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self.stop_sampling.set()
        if (
            self.sampling_thread is not None
            and self.sampling_thread is not threading.current_thread()
        ):
            self.sampling_thread.join(timeout=2.0)
        with self.state_lock:
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

        pool = self.process.read(self.pool_address, self.pool_size)
        if pool is None:
            raise RuntimeError("entity pool became unreadable")
        battle_objects = read_battle_objects(
            self.process,
            self.module.base,
            self.layout.object_count_offset,
            self.layout.object_pointers_offset,
        )
        self.projectile_judgment = projectile_judgment_by_owner(battle_objects)
        player_entities: dict[int, bytes] = {}
        primary_entity_slots: dict[int, int] = {}
        cancel_properties: dict[int, CancelProperties] = {}
        invincibility_properties: dict[int, InvincibilityProperties] = {}
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
                    primary_entity_slots[player] = slot
                    cancel_properties[player] = read_cancel_properties(
                        self.process, entity
                    )
                    invincibility_properties[player] = read_invincibility_properties(
                        self.process, entity
                    )
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
                    "landing_lock_044c": u32(entity, 0x44C),
                    "attack_filter_04b0": u32(entity, 0x4B0),
                    "chip_clear_057c": u32(entity, 0x57C),
                    "move_code_06ac": u32(entity, 0x6AC),
                    "action_instance_0680": u32(entity, 0x680),
                    "vulnerability_0060": u32(entity, 0x60),
                    "hit_filter_04a0": u32(entity, 0x4A0),
                    "descriptor": u32(entity, 0x644),
                    "animation_frame": u32(entity, 0x648),
                    "attack_data": u32(entity, 0x64C),
                    "action_frame": u32(entity, 0x674),
                    "flags_06b8": u32(entity, 0x6B8),
                    "flags_06c8": u32(entity, 0x6C8),
                    "contact_flags_06ac": u32(entity, 0x6AC),
                    "cs_capability_0840": u32(entity, 0x840),
                    "control_state": u32(entity, 0xB6C),
                    "hitstop": u32(entity, 0x1E4),
                    "label": state_label,
                }
            if player in (0, 1) and primary_entity_slots.get(player) == slot:
                debug_entity["cancel_properties"] = cancel_properties[player].debug_dict()
                debug_entity["invincibility_properties"] = (
                    invincibility_properties[player].debug_dict()
                )
            debug_entities.append(debug_entity)

        # The pool and dependent objects take several ReadProcessMemory calls.
        # Accept the snapshot only if the game's logic tick stayed unchanged
        # throughout those essential reads. Otherwise state from tick N+1
        # could be labelled as N and then counted a second time on the next
        # pass, which visibly turns a real 2F active window into 3F.
        raw_tick_after = self.process.read(self.tick_address, 4)
        if raw_tick_after is None:
            raise RuntimeError("battle tick became unreadable")
        if u32(raw_tick_after, 0) != tick:
            return False

        if self.previous_tick is not None and tick < self.previous_tick:
            self.timeline.reset()
            self.semantic_engine.reset()
            self.last_entities = (EMPTY_FRAME, EMPTY_FRAME)
        self.previous_tick = tick

        players: dict[int, FrameBands] = {}
        for player, entity in player_entities.items():
            external_tokens = (
                cancel_properties[player].tokens()
                + invincibility_properties[player].tokens()
            )
            result = self.semantic_engine.classify(
                entity,
                player,
                attack_judgment[player],
                external_tokens=external_tokens,
                world_tokens=("active_projectile",)
                if self.projectile_judgment[player]
                else (),
            )
            players[player] = result.frame
        p1 = players.get(0, EMPTY_FRAME)
        p2 = players.get(1, EMPTY_FRAME)
        actionable = (p1.actionable, p2.actionable)
        if actionable != self.previous_actionable:
            labels = tuple("FREE" if value else "LOCK" for value in actionable)
            print(f"[UNI2 overlay] tick={tick} P1={labels[0]} P2={labels[1]}", flush=True)
            self.previous_actionable = actionable
        self.timeline.push(p1, p2)
        self.last_entities = (p1, p2)
        # Pointer previews are diagnostic-only and intentionally happen after
        # the coherent gameplay snapshot has been committed. They can never
        # alter or duplicate a frame-meter cell.
        if self.debug_capture.active:
            for debug_entity in debug_entities:
                debug_entity["references"] = {
                    "descriptor": self.debug_pointer_preview(
                        int(debug_entity["descriptor"])
                    ),
                    "animation": self.debug_pointer_preview(
                        int(debug_entity["animation_frame"])
                    ),
                    "attack": self.debug_pointer_preview(
                        int(debug_entity["attack_data"])
                    ),
                }
        self.debug_capture.record(
            tick,
            pool,
            {
                "entities": debug_entities,
                # Fireballs and other created battle objects live outside the
                # fixed character entity pool. Preserve their known runtime
                # fields in the JSON sidecar while keeping the U2RG v1 binary
                # capture layout backwards compatible.
                "battle_objects": [
                    item.debug_dict() for item in battle_objects
                ],
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
        self.sample_generation += 1
        return True

    def sampling_loop(self) -> None:
        """Track game logic ticks independently from the Tk renderer."""
        try:
            while not self.stop_sampling.is_set():
                with self.state_lock:
                    changed = self.sample()
                if not changed:
                    # timeBeginPeriod(1) makes this approximately a 1 ms wait,
                    # giving us many observations per 60 Hz game frame without
                    # burning an entire CPU core.
                    time.sleep(0.001)
        except BaseException as error:
            self.sampling_error = error
            self.stop_sampling.set()

    def render(self, width: int, height: int) -> None:
        # Copy the model quickly, then release the sampler before doing the
        # comparatively expensive Tk canvas reconstruction.
        with self.state_lock:
            frames = list(self.timeline.frames)
            current_column = self.timeline.last_written_index
            self.rendered_generation = self.sample_generation
        self.canvas.delete("all")
        if not frames:
            return
        bar_width = min(width - 24, self.timeline_settings.max_width_pixels)
        grid_left = (width - bar_width) // 2
        grid_right = grid_left + bar_width
        gap = 4
        row_height = 52
        first_y = height - (row_height * 2 + gap + 12)
        cell_width = (grid_right - grid_left) / self.timeline.capacity

        for player in range(2):
            y = first_y + player * (row_height + gap)
            for column in range(self.timeline.capacity):
                x0 = grid_left + column * cell_width
                x1 = grid_left + (column + 1) * cell_width - 1
                frame = frames[column][player] if column < len(frames) else EMPTY_FRAME
                self.canvas.create_rectangle(x0, y, x1, y + row_height, fill=EMPTY, outline="")
                # Actionable character-local states remain EMPTY/black, but a
                # live world object can make an otherwise-free frame relevant.
                if frame.relevant:
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

        if self.timeline_settings.show_primary_run_counts:
            for player in range(2):
                row_y = first_y + player * (row_height + gap)
                label_y = row_y - 7 if player == 0 else row_y + row_height + 7
                for run in primary_band_runs(frames, player):
                    center_column = (run.first_column + run.last_column + 1) / 2
                    label_x = grid_left + center_column * cell_width
                    self.canvas.create_text(
                        label_x,
                        label_y,
                        text=str(run.frames),
                        fill=self.timeline_settings.primary_run_count_color,
                        font=(
                            "Segoe UI",
                            self.timeline_settings.primary_run_count_font_size,
                            "bold",
                        ),
                    )

        if current_column is not None:
            cursor_x = grid_left + (current_column + 1) * cell_width - 1
            for player in range(2):
                y = first_y + player * (row_height + gap)
                self.canvas.create_line(
                    cursor_x,
                    y,
                    cursor_x,
                    y + row_height,
                    fill=self.timeline_settings.current_frame_border_color,
                    width=2,
                )

    def update(self) -> None:
        try:
            if self.sampling_error is not None:
                raise RuntimeError("dedicated game-tick sampler failed") from self.sampling_error
            game_is_foreground = foreground_pid() == self.pid
            key_down = bool(
                game_is_foreground
                and user32.GetAsyncKeyState(self.debug_hotkey_code) & 0x8000
            )
            if key_down and not self.debug_key_down:
                with self.state_lock:
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
            with self.state_lock:
                changed = self.sample_generation != self.rendered_generation
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
        # Rendering is intentionally paced separately from game-state reads.
        self.root.after(4, self.update)

    def run(self) -> None:
        self.timer_resolution_active = winmm.timeBeginPeriod(1) == 0
        try:
            self.sampling_thread = threading.Thread(
                target=self.sampling_loop,
                name="UNI2TickSampler",
                daemon=True,
            )
            self.sampling_thread.start()
            self.update()
            if self.duration is not None:
                self.root.after(max(1, int(self.duration * 1000)), self.close)
            self.root.mainloop()
        finally:
            if self.timer_resolution_active:
                winmm.timeEndPeriod(1)
                self.timer_resolution_active = False


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
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_PROFILE,
        help="semantic and timeline config (default: ./frame_semantics.json)",
    )
    args = parser.parse_args()
    print(
        f"[UNI2 overlay] build={BUILD_ID}; mode={'raw' if args.raw_states else 'confirmed'}; "
        f"debug={args.debug_hotkey.upper()}; live display controls enabled; "
        f"config={args.config.resolve()}"
    )
    if not args.raw_states:
        startup_engine = SemanticEngine(profile=args.config)
        print(
            "[UNI2 overlay] colors: "
            f"N={startup_engine.colors['normal_cancel']} "
            f"SP={startup_engine.colors['special_cancel']} "
            f"EX={startup_engine.colors['ex_cancel']} "
            f"CS={startup_engine.colors['cs_cancel']} "
            f"FULL={startup_engine.colors['full_invincible']} "
            f"THROW={startup_engine.colors['throw_invincible']}"
        )
    Overlay(
        args.duration,
        raw_states=args.raw_states,
        debug_hotkey=args.debug_hotkey,
        log_dir=args.log_dir,
        profile=args.config,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
