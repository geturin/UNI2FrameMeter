from __future__ import annotations

import argparse
import colorsys
import ctypes
from ctypes import wintypes
from copy import deepcopy
import hashlib
import json
import os
import sys
from pathlib import Path
import struct
import threading
import time
import tkinter as tk

from combat_properties import (
    CancelProperties,
    InvincibilityProperties,
    guard_direction_by_player,
    read_cancel_properties,
    read_invincibility_properties,
)
from battle_objects import (
    projectile_judgment_by_owner,
    read_battle_objects,
)
from debug_capture import DebugCapture
from display_config import DisplayConfig
from display_controls import DisplayControls
from frame_timeline import (
    EMPTY_FRAME,
    FrameBands,
    FrameTimeline,
    TimelineSettings,
    primary_band_runs,
)
from semantic_engine import DEFAULT_PROFILE, SemanticEngine
from runtime_layout import (
    ENTITY_COUNT, ENTITY_STRIDE, PLAYER_OFFSET, ACTIVE_OFFSET, ANIMATION_OFFSET,
    DESCRIPTOR_OFFSET, ATTACK_OFFSET, MOVABLE_OFFSET, LANDING_LOCK_OFFSET,
    MOVE_CODE_OFFSET, ACTION_FRAME_OFFSET, ACTION_INSTANCE_OFFSET, GUARD_PLUS_OFFSET,
    HIT_FILTER_OFFSET, ATTACK_FILTER_OFFSET, HITSTOP_OFFSET, LABEL_OFFSET, LABEL_BYTES,
    PHASE_STATE_OFFSET, SLOW_SKIP_OFFSET, GLOBAL_STOP_OFFSET, SCENE_CLOCK_OFFSET,
)
from hook_client import HookClient, NativeSnapshot, FM_VALID, FM_RESET, FM_SUSPENDED
from app_errors import APP_TITLE, default_log_directory, report_error
from process_memory import require_process


TRANSPARENT = "#010203"
GRID = "#313844"
EMPTY = "#080a0e"
LOCKED = "#cf3f83"
HITSTOP = "#f3c64d"
BUILD_ID = "v0.6.0"
ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]


def print(*args, **kwargs):
    """PyInstaller windowed builds intentionally have no stdout."""
    if sys.stdout is not None:
        import builtins
        builtins.print(*args, **kwargs)

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

# Explicit pointer-width declarations are required by the 64-bit overlay.
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetClientRect.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
user32.ClientToScreen.restype = wintypes.BOOL
user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetParent.argtypes = [wintypes.HWND]
user32.GetParent.restype = wintypes.HWND
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = wintypes.LONG
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
user32.SetWindowLongW.restype = wintypes.LONG
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL


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
    def __init__(self, *args, **kwargs):
        self.process = None
        self.hook_client = None
        self.root = None
        self.closed = False
        self.failed = False
        try:
            self._initialize(*args, **kwargs)
        except BaseException:
            if self.hook_client is not None:
                self.hook_client.close()
            if self.process is not None:
                self.process.close()
            if self.root is not None:
                self.root.destroy()
            raise

    def _initialize(
        self,
        duration: float | None = None,
        raw_states: bool = False,
        debug_hotkey: str = "F8",
        log_dir: Path | None = None,
        profile: Path = DEFAULT_PROFILE,
    ):
        function_key_code(debug_hotkey)
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
        self.pid, self.process, self.module, digest = require_process()
        self.game_hwnd = game_window(self.pid)
        if not self.game_hwnd:
            self.process.close()
            raise RuntimeError("unable to find the UNI2 game window")

        self.hook_client = HookClient(self.pid, self.module.base, digest, ROOT)
        self.layout = self.hook_client.layout
        print(f"[UNI2 overlay] native hook=+0x{self.layout.hook_offset:X}; stride=0x{self.layout.entity_stride:X}", flush=True)
        self.pool_address = self.module.base + self.layout.entity_pool_offset
        self.pool_size = self.layout.entity_stride * self.layout.entity_count
        self.native_tick_gaps = 0
        self.native_rejected_packets = 0
        self.incomplete_packets = 0
        self.previous_invalid_packets = self.hook_client.invalid_packets
        self.previous_tick: int | None = None
        self.last_native_status: int | None = None
        self.previous_actionable: tuple[bool, bool] | None = None
        self.duration = duration
        self.raw_states = raw_states
        self.debug_hotkey = debug_hotkey.upper()
        self.debug_hotkey_code = function_key_code(debug_hotkey)
        self.debug_key_down = False
        self.debug_capture = DebugCapture(
            log_dir if log_dir is not None else default_log_directory(),
            self.layout.entity_pool_offset,
            self.pool_size,
            self.layout.battle_tick_offset,
            digest,
            BUILD_ID,
            "raw" if raw_states else "confirmed",
        )

        self.root = tk.Tk()
        self.root.report_callback_exception = self.callback_exception
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
        self.control_window.title(APP_TITLE)
        self.control_window.resizable(False, False)
        self.control_window.attributes("-topmost", True)
        self.control_window.protocol("WM_DELETE_WINDOW", self.close)
        self.display_controls = DisplayControls(
            self.control_window,
            self.display_config.items(),
            self.semantic_colors,
            self.toggle_display,
            labels={token: style.get("label", token) for token, style in self.semantic_engine.token_styles.items()},
        )
        self.display_controls.grid(row=0, column=0, sticky="nsew")
        self.display_variables = self.display_controls.variables
        self.status_variable = self.display_controls.status_variable
        self.control_window.update_idletasks()
        self.capture_status = "Waiting for Training Mode"
        self.capture_status_until: float | None = None
        self.display_controls.show_status(self.capture_status)
        self.control_window.geometry("+20+20")

    def toggle_display(self, token: str) -> None:
        variable = self.display_variables[token]
        display = bool(variable.get())
        old_display = next(item.display for item in self.display_config.items() if item.token == token)
        try:
            with self.state_lock:
                old_document = deepcopy(self.display_config.document)
                old_external = self.semantic_engine.external_attributes.copy()
                old_runtime = self.semantic_engine.runtime_attributes
                try:
                    self.semantic_engine.set_attribute_display(token, display)
                    self.display_config.set_display(token, display)
                except (OSError, ValueError, KeyError):
                    self.display_config.document = old_document
                    self.semantic_engine.external_attributes = old_external
                    self.semantic_engine.runtime_attributes = old_runtime
                    raise
                # Existing cells were classified under the former visibility
                # set. Clear them so the checkbox is effective immediately.
                self.timeline.reset()
                self.semantic_engine.reset()
                self.previous_actionable = None
                self.sample_generation += 1
        except (OSError, ValueError, KeyError) as error:
            variable.set(old_display)
            self.display_controls.refresh_swatch(token)
            report_error(error)
            return
        self.display_controls.refresh_swatch(token)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self.stop_sampling.set()
        if self.sampling_thread is not None and self.sampling_thread is not threading.current_thread():
            self.sampling_thread.join(timeout=2.0)
        error = None
        try:
            with self.state_lock:
                path = self.debug_capture.stop()
            if path is not None:
                print(f"[UNI2 overlay] debug recording stopped: {path.resolve()}", flush=True)
        except Exception as failure:
            error = failure
        finally:
            self.hook_client.close()
            self.process.close()
            self.root.destroy()
        if error is not None and not self.failed:
            self.failed = True
            report_error(error)

    def callback_exception(self, exc_type, error, traceback) -> None:
        error = error.with_traceback(traceback)
        self.fail(error)

    def fail(self, error: BaseException) -> None:
        if self.failed:
            return
        self.failed = True
        self.close()
        report_error(error)

    def debug_pointer_preview(self, snapshot: NativeSnapshot, pointer: int, size: int = 0x60) -> dict[str, object] | None:
        if not pointer:
            return None
        raw = snapshot.read(pointer, size)
        if raw is None:
            return {"pointer": pointer, "readable": False, "reason": "not_captured_in_native_packet"}
        text = raw.split(b"\0", 1)[0].decode("cp932", errors="replace")
        return {
            "pointer": pointer,
            "readable": True,
            "hash": hashlib.blake2s(raw, digest_size=8).hexdigest(),
            "head": raw.hex(),
            "text": text,
        }

    def reset_display(self, message: str) -> None:
        self.timeline.reset()
        self.semantic_engine.reset()
        self.last_entities = (EMPTY_FRAME, EMPTY_FRAME)
        self.previous_tick = None
        self.previous_actionable = None
        self.capture_status = message
        self.capture_status_until = time.monotonic() + 2.0
        self.sample_generation += 1

    def sample(self) -> bool:
        packets = self.hook_client.read_available()
        changed = False
        rejected_delta = (self.hook_client.invalid_packets - self.previous_invalid_packets) & 0xFFFFFFFF
        self.previous_invalid_packets = self.hook_client.invalid_packets
        if rejected_delta:
            self.native_rejected_packets += rejected_delta
            self.reset_display("Capture reset")
            changed = True
        if self.hook_client.status == FM_SUSPENDED:
            if self.last_native_status != FM_SUSPENDED:
                self.reset_display("Waiting for Training Mode")
                self.capture_status_until = None
                changed = True
            self.last_native_status = FM_SUSPENDED
            return changed
        self.last_native_status = self.hook_client.status
        for snapshot in packets:
            if snapshot.dropped_before:
                self.reset_display("Frame gap · timeline reset")
            if snapshot.flags & FM_RESET:
                self.reset_display("Capture reset")
            if not snapshot.flags & FM_VALID:
                continue
            changed = self.sample_snapshot(snapshot) or changed
        return changed

    def sample_snapshot(self, snapshot: NativeSnapshot) -> bool:
        tick = snapshot.tick
        if tick == self.previous_tick:
            return False
        pool = snapshot.read(self.pool_address, self.pool_size)
        if pool is None:
            raise RuntimeError("Native frame snapshot does not contain the complete entity pool")
        battle_objects = read_battle_objects(
            snapshot,
            self.module.base,
            self.layout.object_count_offset,
            self.layout.object_pointers_offset,
        )
        if any(item.active_marker and item.object_type == 2 and item.owner in (0, 1) and item.frame_attack_data_pointer is None for item in battle_objects):
            self.incomplete_packets += 1
            self.reset_display("Capture reset")
            return False
        self.projectile_judgment = projectile_judgment_by_owner(battle_objects)
        player_entities: dict[int, bytes] = {}
        primary_entity_slots: dict[int, int] = {}
        cancel_properties: dict[int, CancelProperties] = {}
        invincibility_properties: dict[int, InvincibilityProperties] = {}
        attack_judgment = {0: False, 1: False}
        debug_entities: list[dict[str, object]] = []
        for slot in range(self.layout.entity_count):
            start = slot * self.layout.entity_stride
            entity = pool[start : start + self.layout.entity_stride]
            if not entity[ACTIVE_OFFSET]:
                continue
            player = entity[PLAYER_OFFSET]
            if player in (0, 1):
                if player not in player_entities:
                    player_entities[player] = entity
                    primary_entity_slots[player] = slot
                    cancel_properties[player] = read_cancel_properties(
                        snapshot, entity
                    )
                    invincibility_properties[player] = read_invincibility_properties(
                        snapshot, entity
                    )
                attack_judgment[player] = bool(
                    attack_judgment[player] or u32(entity, ATTACK_OFFSET)
                )
            state_label = entity[LABEL_OFFSET:LABEL_OFFSET + LABEL_BYTES].split(b"\0", 1)[0].decode(
                "ascii", errors="replace"
            )
            debug_entity: dict[str, object] = {
                    "slot": slot,
                    "player": player,
                    "character_id": entity[0x05],
                    "data_delay_0024": struct.unpack_from("<H", entity, 0x24)[0],
                    "movable": entity[MOVABLE_OFFSET],
                    "landing_lock": struct.unpack_from("<i", entity, LANDING_LOCK_OFFSET)[0],
                    "attack_filter": u32(entity, ATTACK_FILTER_OFFSET),

                    "move_code": u32(entity, MOVE_CODE_OFFSET),
                    "action_instance": u32(entity, ACTION_INSTANCE_OFFSET),
                    "raw_u32_0060": u32(entity, 0x60),
                    "hit_filter": u32(entity, HIT_FILTER_OFFSET),
                    "guard_plus": entity[GUARD_PLUS_OFFSET],
                    "descriptor": u32(entity, DESCRIPTOR_OFFSET),
                    "animation_frame": u32(entity, ANIMATION_OFFSET),
                    "attack_data": u32(entity, ATTACK_OFFSET),
                    "action_frame": u32(entity, ACTION_FRAME_OFFSET),
                    "control_state": None,
                    "hitstop": struct.unpack_from("<h", entity, HITSTOP_OFFSET)[0],
                    "label": state_label,
                }
            if player in (0, 1) and primary_entity_slots.get(player) == slot:
                debug_entity["cancel_properties"] = cancel_properties[player].debug_dict()
                debug_entity["invincibility_properties"] = (
                    invincibility_properties[player].debug_dict()
                )
            debug_entities.append(debug_entity)

        if any(value.read_error for value in cancel_properties.values()) or any(value.read_error for value in invincibility_properties.values()):
            self.incomplete_packets += 1
            self.reset_display("Capture reset")
            return False
        guard_direction_properties = guard_direction_by_player(player_entities)
        for debug_entity in debug_entities:
            player = debug_entity["player"]
            if primary_entity_slots.get(player) != debug_entity["slot"]:
                continue
            guard = guard_direction_properties[player]
            debug_entity["guard_direction_properties"] = {
                **guard.debug_dict(),
                "source_slot": primary_entity_slots.get(guard.source_player),
            }

        if self.previous_tick is not None and tick < self.previous_tick:
            self.reset_display("Capture reset")
        elif self.previous_tick is not None and tick > self.previous_tick + 1:
            self.native_tick_gaps += tick - self.previous_tick - 1
            self.reset_display("Frame gap · timeline reset")
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
                native_actionable=cancel_properties[player].native_actionable,
                status_tokens=(
                    guard_direction_properties[player].tokens()
                    + cancel_properties[player].posture_tokens()
                ),
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
        # Preview only chunks already present in this immutable native packet.
        # Missing optional bytes are reported instead of reading live pointers.
        if self.debug_capture.active:
            for debug_entity in debug_entities:
                debug_entity["references"] = {
                    "descriptor": self.debug_pointer_preview(
                        snapshot, int(debug_entity["descriptor"])
                    ),
                    "animation": self.debug_pointer_preview(
                        snapshot, int(debug_entity["animation_frame"])
                    ),
                    "attack": self.debug_pointer_preview(
                        snapshot, int(debug_entity["attack_data"])
                    ),
                }
        clock_raw = snapshot.read(self.module.base + SCENE_CLOCK_OFFSET, 0x1C)
        phase_raw = snapshot.read(self.module.base + PHASE_STATE_OFFSET, 12)
        slow_raw = snapshot.read(self.module.base + SLOW_SKIP_OFFSET, 4)
        global_stop_raw = snapshot.read(self.module.base + GLOBAL_STOP_OFFSET, 4)
        self.debug_capture.record(
            tick,
            pool,
            {
                "entities": debug_entities,
                "native_sequence": snapshot.sequence,
                "native_elapsed_tick": snapshot.tick,
                "native_elapsed": snapshot.tick,
                "phase_id": u32(phase_raw, 0) if phase_raw is not None else None,
                "phase_tick": u32(phase_raw, 8) if phase_raw is not None else None,
                "slow_skip": u32(slow_raw, 0) if slow_raw is not None else None,
                "global_stop": u32(global_stop_raw, 0) if global_stop_raw is not None else None,
                "native_clock_raw": list(struct.unpack("<7I", clock_raw)) if clock_raw is not None else None,
                "native_phase_state_raw": list(struct.unpack("<3I", phase_raw)) if phase_raw is not None else None,
                "native_slow_skip_raw": u32(slow_raw, 0) if slow_raw is not None else None,
                "native_global_stop_raw": u32(global_stop_raw, 0) if global_stop_raw is not None else None,
                "native_scene": snapshot.scene,
                "dropped_frames": self.hook_client.dropped_frames,
                "native_tick_gaps": self.native_tick_gaps,
                "native_rejected_packets": self.native_rejected_packets,
                "incomplete_packets": self.incomplete_packets,
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
                        "move_code": u32(player_entities[player], MOVE_CODE_OFFSET)
                        if player in player_entities else None,
                    }
                    for player in (0, 1)
                ],
            },
        )
        if self.capture_status == "Waiting for Training Mode":
            self.capture_status = ""
            self.capture_status_until = None
        self.sample_generation += 1
        return True

    def sampling_loop(self) -> None:
        """Consume every native-hook packet independently from Tk rendering."""
        try:
            while not self.stop_sampling.is_set():
                with self.state_lock:
                    changed = self.sample()
                if not changed:
                    # The producer owns game timing. This wait only paces
                    # shared-memory consumption; it does not resample gameplay.
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
                # Independent buffs and live world objects can make an
                # otherwise-free frame relevant without changing actionability.
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
            if not self.process.is_running():
                self.close()
                return
            if self.sampling_error is not None:
                raise RuntimeError(f"Native snapshot reader failed: {self.sampling_error}") from self.sampling_error
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
                if self.capture_status_until is not None and time.monotonic() >= self.capture_status_until:
                    self.capture_status = ""
                    self.capture_status_until = None
                status = self.capture_status
            self.display_controls.show_status(status)
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
        except Exception as error:
            self.fail(error)
            return
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
            self.close()
            if self.timer_resolution_active:
                winmm.timeEndPeriod(1)
                self.timer_resolution_active = False


def main() -> int:
    parser = argparse.ArgumentParser(description="Native hook UNI2 frame-meter overlay")
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
        default=default_log_directory(),
        help="debug recording directory (default: %LOCALAPPDATA%/UNI2FrameMeter/logs)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_PROFILE,
        help="semantic and timeline config (default: ./frame_semantics.json)",
    )
    parser.add_argument("--self-check", action="store_true", help="validate the portable package without starting or attaching to the game")
    parser.add_argument("--self-check-report", type=Path, help="write the self-check result as UTF-8 JSON")
    args = parser.parse_args()
    if args.self_check:
        from self_check import check_package
        report = check_package(ROOT, args.config, BUILD_ID)
        if args.self_check_report is not None:
            args.self_check_report.parent.mkdir(parents=True, exist_ok=True)
            args.self_check_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        return 0
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
    overlay = Overlay(
        args.duration,
        raw_states=args.raw_states,
        debug_hotkey=args.debug_hotkey,
        log_dir=args.log_dir,
        profile=args.config,
    )
    overlay.run()
    return 1 if overlay.failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        report_error(error, show_dialog="--self-check" not in sys.argv)
        raise SystemExit(1)
