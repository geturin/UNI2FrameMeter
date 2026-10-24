#!/usr/bin/env python3
"""Verify the supplied game EXE against the audited profile without running it."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / "compatibility/2026-10-24.json"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PeImage:
    def __init__(self, data: bytes):
        self.data = data
        if len(data) < 64 or data[:2] != b"MZ":
            raise ValueError("Not a valid MZ image")
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if pe < 64 or pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("Invalid PE header bounds or signature")
        self.machine, count, self.timestamp = struct.unpack_from("<HHI", data, pe + 4)
        optional_bytes = struct.unpack_from("<H", data, pe + 20)[0]
        opt = pe + 24
        table = opt + optional_bytes
        if optional_bytes < 96 or table > len(data) or not 0 < count <= 96 or table + count * 40 > len(data):
            raise ValueError("Invalid PE optional header or section table")
        self.magic = struct.unpack_from("<H", data, opt)[0]
        self.image_size = struct.unpack_from("<I", data, opt + 56)[0]
        self.sections = []
        for index in range(count):
            virtual_bytes, rva, raw_bytes, offset = struct.unpack_from("<4I", data, table + index * 40 + 8)
            if offset + raw_bytes > len(data):
                raise ValueError("A PE section exceeds the file bounds")
            self.sections.append((rva, virtual_bytes, raw_bytes, offset))

    def at_rva(self, rva: int, size: int) -> bytes:
        if rva < 0 or size <= 0:
            raise ValueError("Invalid requested code-window bounds")
        matches = []
        for start, _virtual_bytes, raw_bytes, offset in self.sections:
            delta = rva - start
            if 0 <= delta and delta + size <= raw_bytes:
                matches.append(self.data[offset + delta:offset + delta + size])
        if len(matches) != 1:
            raise ValueError(f"RVA {rva:#x} does not have one file-backed section")
        return matches[0]


def check_profile(path: Path, root: Path = ROOT) -> dict[str, object]:
    """Return identity, source consistency and audited code-window checks."""
    profile = json.loads((root / PROFILE.relative_to(ROOT)).read_text(encoding="utf-8"))
    data = path.read_bytes()
    image = PeImage(data)
    source = (root / "native/profile.h").read_text(encoding="utf-8")
    constants = {name: int(value, 0) for name, value in re.findall(
        r"constexpr uint32_t (FM_\w+) = (0x[0-9a-fA-F]+|\d+);", source)}
    native_hash = re.search(r'FM_GAME_SHA256\[\] = "([0-9a-f]{64})"', source)
    client_hash = re.search(r'SUPPORTED_SHA256 = "([0-9a-f]{64})"',
                            (root / "src/hook_client.py").read_text(encoding="utf-8"))
    hook_source = re.search(r"FM_HOOK_BYTES\[\] = \{(.*?)\};", source, re.S)
    if not native_hash or not client_hash or not hook_source:
        raise ValueError("The runtime profile declarations could not be read")
    hook = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]+)", hook_source[1]))
    layout = {}
    for node in ast.parse((root / "src/runtime_layout.py").read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            layout[node.targets[0].id] = ast.literal_eval(node.value)
    # JSON normalizes the tuple timer fields to lists.
    layout = json.loads(json.dumps(layout))
    digest = _digest(data)
    checks = {
        "game_sha256": digest == profile["game_sha256"],
        "file_bytes": len(data) == profile["file_bytes"],
        "machine": image.machine == int(profile["machine"], 0),
        "optional_magic": image.magic == int(profile["optional_magic"], 0),
        "image_size": image.image_size == int(profile["image_size"], 0),
        "image_timestamp": image.timestamp == int(profile["image_timestamp"], 0),
        "runtime_hashes": native_hash[1] == client_hash[1] == profile["game_sha256"],
        "native_constants": constants == profile["native_constants"],
        "python_layout": layout == profile["python_layout"],
        "hook_entry": bool(hook) and image.at_rva(constants["FM_HOOK_RVA"], len(hook)) == hook,
    }
    windows = {}
    for item in profile["code_windows"]:
        actual = _digest(image.at_rva(int(item["rva"], 0), item["bytes"]))
        windows[item["name"]] = actual == item["sha256"]
    return {"ok": all(checks.values()) and all(windows.values()),
            "exe_sha256": digest, "checks": checks, "code_windows": windows,
            "game_started": False, "hook_installed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path, help="Path to uni2.exe")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    args = parser.parse_args()
    try:
        report = check_profile(args.exe)
    except (OSError, ValueError, KeyError, struct.error, SyntaxError) as error:
        report = {"ok": False, "error": str(error), "game_started": False, "hook_installed": False}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("PASS: audited game profile" if report["ok"] else "FAIL: unsupported or inconsistent game profile")
        if "error" in report:
            print(report["error"])
        for group in ("checks", "code_windows"):
            for name, passed in report.get(group, {}).items():
                if not passed:
                    print("Failed:", name)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
