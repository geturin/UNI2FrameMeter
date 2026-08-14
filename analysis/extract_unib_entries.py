from __future__ import annotations

import argparse
from pathlib import Path
import re

from list_unib_index import parse_index


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract selected UNI2 index entries")
    parser.add_argument("index", type=Path)
    parser.add_argument("--match", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    archive_name, entries = parse_index(args.index)
    archive_path = args.index.parent / archive_name
    pattern = re.compile(args.match, re.IGNORECASE)
    selected = [entry for entry in entries if pattern.search(entry.logical_path)]
    if not selected:
        raise RuntimeError("no index entries matched")

    archive_size = archive_path.stat().st_size
    with archive_path.open("rb") as archive:
        for entry in selected:
            if entry.offset + entry.stored_size > archive_size:
                raise RuntimeError(f"entry exceeds archive: {entry.logical_path}")
            archive.seek(entry.offset)
            data = archive.read(entry.stored_size)
            if len(data) != entry.stored_size:
                raise RuntimeError(f"short read: {entry.logical_path}")

            relative = Path(*entry.logical_path.split("/"))
            destination = (args.out / relative).resolve()
            output_root = args.out.resolve()
            if output_root not in destination.parents:
                raise RuntimeError(f"unsafe output path: {entry.logical_path}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            print(f"{entry.logical_path} -> {destination} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
