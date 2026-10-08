"""Portable-package validation without process enumeration or injection."""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct

from hook_client import ABI, HEADER_BYTES, SLOT_BYTES, CAPACITY, DATA_OFFSET, MAPPING_BYTES, NATIVE_HOST_NAME, NATIVE_DLL_NAME, SUPPORTED_SHA256
from semantic_engine import SemanticEngine
from frame_timeline import TimelineSettings
from display_config import DisplayConfig


def _pe32(path: Path, expect_dll: bool) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 64 or data[:2] != b"MZ":
        raise RuntimeError(f"Native package file is not a PE image: {path.name}")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if pe + 120 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        raise RuntimeError(f"Native package file has an invalid PE header: {path.name}")
    machine, sections, _time, _symbols, _symbol_count, optional_size, flags = struct.unpack_from("<HHIIIHH", data, pe + 4)
    optional = pe + 24
    if machine != 0x14C or struct.unpack_from("<H", data, optional)[0] != 0x10B or bool(flags & 0x2000) != expect_dll:
        raise RuntimeError(f"Native package file has the wrong architecture or type: {path.name}")
    section_table = optional + optional_size
    if not 0 < sections <= 96 or section_table + sections * 40 > len(data):
        raise RuntimeError(f"Native package file has invalid section bounds: {path.name}")
    if expect_dll:
        export_rva, export_size = struct.unpack_from("<II", data, optional + 96)
        if not export_rva or export_size < 40:
            raise RuntimeError("FrameMeter DLL has no export directory")
        def at_rva(rva: int, size: int) -> bytes:
            for i in range(sections):
                sec = section_table + i * 40
                virtual_size, virtual_rva, raw_size, raw_offset = struct.unpack_from("<4I", data, sec + 8)
                delta = rva - virtual_rva
                if 0 <= delta and delta + size <= raw_size and raw_offset + delta + size <= len(data):
                    return data[raw_offset + delta:raw_offset + delta + size]
            raise RuntimeError("FrameMeter DLL export is outside its file bounds")
        directory = at_rva(export_rva, 40)
        names_count, names_rva = struct.unpack_from("<I", directory, 24)[0], struct.unpack_from("<I", directory, 32)[0]
        if not 0 < names_count <= 512:
            raise RuntimeError("FrameMeter DLL export count is invalid")
        name_rvas = at_rva(names_rva, names_count * 4)
        exports = set()
        for (rva,) in struct.iter_unpack("<I", name_rvas):
            name = bytearray()
            for offset in range(256):
                char = at_rva(rva + offset, 1)
                if char == b"\0":
                    exports.add(bytes(name).decode("ascii", errors="strict"))
                    break
                name.extend(char)
        if "FrameMeterStart" not in exports:
            raise RuntimeError("FrameMeter DLL is missing its FrameMeterStart entry")
    return {"path": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "machine": "x86", "dll": expect_dll}


def check_package(directory: Path, profile: Path, build_id: str) -> dict[str, object]:
    if HEADER_BYTES != 256 or DATA_OFFSET != 7232 or MAPPING_BYTES != HEADER_BYTES + SLOT_BYTES * CAPACITY:
        raise RuntimeError("FrameMeter shared-memory ABI is inconsistent")
    engine = SemanticEngine(profile)
    settings = TimelineSettings.load(profile)
    display = DisplayConfig.load(profile)
    if not engine.colors or settings.length_frames <= 0 or not display.items():
        raise RuntimeError("FrameMeter display configuration is incomplete")
    files = [_pe32(directory / NATIVE_HOST_NAME, False), _pe32(directory / NATIVE_DLL_NAME, True)]
    return {"ok": True, "build": build_id, "abi": ABI, "mapping_bytes": MAPPING_BYTES,
            "slot_bytes": SLOT_BYTES, "capacity": CAPACITY, "supported_exe_sha256": SUPPORTED_SHA256,
            "profile": str(profile.resolve()), "display_switches": len(display.items()), "files": files,
            "game_started": False, "hook_installed": False}
