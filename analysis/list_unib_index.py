from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import struct


@dataclass(frozen=True)
class Entry:
    folder: str
    filename: str
    decompressed_size: int
    stored_size: int
    offset: int

    @property
    def logical_path(self) -> str:
        return f"{self.folder}/{self.filename}".replace("\\", "/")


def c_string(data: bytes) -> str:
    return data.split(b"\0", 1)[0].decode("ascii", errors="replace")


def parse_index(path: Path) -> tuple[str, list[Entry]]:
    data = path.read_bytes()
    if len(data) < 64:
        raise ValueError(f"index is too small: {path}")
    folder_count, file_count, _archive_size = struct.unpack_from("<iiI", data, 0)
    archive_name = c_string(data[12:64])
    if not (0 <= folder_count <= 100_000 and 0 <= file_count <= 10_000_000):
        raise ValueError(f"implausible index counts in {path}")

    cursor = 64
    folders: list[tuple[int, str]] = []
    for _ in range(folder_count):
        files_in_folder, _unknown1, _unknown2 = struct.unpack_from("<iii", data, cursor)
        folder_name = c_string(data[cursor + 12 : cursor + 128])
        folders.append((files_in_folder, folder_name))
        cursor += 128
    cursor += 4

    raw_entries: list[tuple[int, int, int, str]] = []
    for _ in range(file_count):
        decompressed, stored, offset = struct.unpack_from("<iiI", data, cursor)
        filename = c_string(data[cursor + 12 : cursor + 76])
        raw_entries.append((decompressed, stored, offset, filename))
        cursor += 80

    entries: list[Entry] = []
    entry_index = 0
    for files_in_folder, folder_name in folders:
        for _ in range(files_in_folder):
            if entry_index >= len(raw_entries):
                raise ValueError("folder counts exceed file count")
            decompressed, stored, offset, filename = raw_entries[entry_index]
            entries.append(Entry(folder_name, filename, decompressed, stored, offset))
            entry_index += 1
    return archive_name, entries


def main() -> int:
    parser = argparse.ArgumentParser(description="List a UNI2 package index without extracting")
    parser.add_argument("index", type=Path)
    parser.add_argument("--match", default="")
    args = parser.parse_args()

    archive_name, entries = parse_index(args.index)
    pattern = re.compile(args.match, re.IGNORECASE) if args.match else None
    print(f"index={args.index}")
    print(f"archive={archive_name}")
    print(f"entries={len(entries)}")
    for entry in entries:
        if pattern is not None and pattern.search(entry.logical_path) is None:
            continue
        print(
            f"{entry.offset:10d} {entry.stored_size:9d} {entry.decompressed_size:9d} "
            f"{entry.logical_path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
