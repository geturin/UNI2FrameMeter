from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import struct
import sys
from typing import BinaryIO


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from list_unib_index import Entry, parse_index  # noqa: E402


INDEX_HEADER_SIZE = 64
FOLDER_RECORD_SIZE = 128
ENTRY_RECORD_SIZE = 80


@dataclass(frozen=True)
class Replacement:
    logical_path: str
    source: Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def entry_record_offset(index_data: bytes, entry_number: int) -> int:
    folder_count = struct.unpack_from("<i", index_data, 0)[0]
    return (
        INDEX_HEADER_SIZE
        + folder_count * FOLDER_RECORD_SIZE
        + 4
        + entry_number * ENTRY_RECORD_SIZE
    )


def copy_exact(source: BinaryIO, destination: BinaryIO, size: int) -> None:
    remaining = size
    while remaining:
        chunk = source.read(min(1024 * 1024, remaining))
        if not chunk:
            raise RuntimeError(f"source archive ended with {remaining} bytes remaining")
        destination.write(chunk)
        remaining -= len(chunk)


def rebuild(
    index_path: Path,
    output_index: Path,
    output_archive: Path,
    replacements: dict[str, Path],
) -> tuple[list[Entry], str]:
    archive_name, entries = parse_index(index_path)
    source_archive = index_path.parent / archive_name
    if not source_archive.is_file():
        raise FileNotFoundError(source_archive)

    normalized = {name.replace("/", "\\").lower(): path for name, path in replacements.items()}
    known = {entry.logical_path.replace("/", "\\").lower() for entry in entries}
    missing = sorted(set(normalized) - known)
    if missing:
        raise ValueError(f"replacement paths are absent from index: {missing}")

    output_index.parent.mkdir(parents=True, exist_ok=True)
    output_archive.parent.mkdir(parents=True, exist_ok=True)
    index_data = bytearray(index_path.read_bytes())
    rewritten: list[Entry] = []
    offset = 0

    with source_archive.open("rb") as source, output_archive.open("wb") as destination:
        for number, entry in enumerate(entries):
            key = entry.logical_path.replace("/", "\\").lower()
            replacement = normalized.get(key)
            if replacement is None:
                source.seek(entry.offset)
                copy_exact(source, destination, entry.stored_size)
                size = entry.stored_size
            else:
                data = replacement.read_bytes()
                destination.write(data)
                size = len(data)

            rewritten_entry = Entry(
                folder=entry.folder,
                filename=entry.filename,
                decompressed_size=size,
                stored_size=size,
                offset=offset,
            )
            rewritten.append(rewritten_entry)
            record = entry_record_offset(index_data, number)
            struct.pack_into("<iiI", index_data, record, size, size, offset)
            offset += size

    struct.pack_into("<I", index_data, 8, offset)
    archive_name_bytes = output_archive.name.encode("ascii")
    if len(archive_name_bytes) >= 52:
        raise ValueError("output archive filename is too long for index header")
    index_data[12:64] = archive_name_bytes.ljust(52, b"\0")
    output_index.write_bytes(index_data)

    parsed_name, parsed_entries = parse_index(output_index)
    if parsed_name != output_archive.name or parsed_entries != rewritten:
        raise RuntimeError("rebuilt index failed round-trip validation")
    if output_archive.stat().st_size != offset:
        raise RuntimeError("rebuilt archive size does not match rebuilt index")
    return rewritten, sha256(output_archive)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild an uncompressed UNI2 archive and all affected index offsets"
    )
    parser.add_argument("index", type=Path)
    parser.add_argument("--output-index", type=Path, required=True)
    parser.add_argument("--output-archive", type=Path, required=True)
    parser.add_argument(
        "--replace",
        nargs=2,
        action="append",
        metavar=("LOGICAL_PATH", "FILE"),
        default=[],
    )
    args = parser.parse_args()
    replacements = {logical: Path(path) for logical, path in args.replace}
    entries, digest = rebuild(
        args.index, args.output_index, args.output_archive, replacements
    )
    print(f"entries={len(entries)}")
    print(f"archive_size={args.output_archive.stat().st_size}")
    print(f"archive_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
