"""Visible errors and writable UTF-8 logs for the windowed Windows build."""
from __future__ import annotations

import ctypes
from datetime import datetime
import os
from pathlib import Path
import sys
import tempfile
import traceback

APP_TITLE = "UNI2 Frame Meter"


def user_data_directory() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "UNI2FrameMeter"


def default_log_directory() -> Path:
    return user_data_directory() / "logs"


def write_error(error: BaseException) -> Path | None:
    detail = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    for directory in (default_log_directory(), Path(tempfile.gettempdir()) / "UNI2FrameMeter-logs"):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"error-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.log"
            path.write_text(detail, encoding="utf-8")
            return path
        except OSError:
            continue
    return None


def report_error(error: BaseException, show_dialog: bool = True) -> Path | None:
    path = write_error(error)
    body = str(error) or type(error).__name__
    body += f"\n\nLog: {path}" if path is not None else "\n\nThe error log could not be saved."
    if sys.stderr is not None:
        print(body, file=sys.stderr, flush=True)
    if show_dialog and os.name == "nt":
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.MessageBoxW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        user32.MessageBoxW.restype = ctypes.c_int
        user32.MessageBoxW(None, body, APP_TITLE, 0x10 | 0x10000)
    return path
