from __future__ import annotations

from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from list_unib_index import parse_index  # noqa: E402
from repack_unib_archive import rebuild  # noqa: E402


def make_index(path: Path, archive_name: str) -> None:
    data = bytearray(64 + 128 + 4 + 2 * 80)
    struct.pack_into("<iiI", data, 0, 1, 2, 7)
    data[12:64] = archive_name.encode("ascii").ljust(52, b"\0")
    struct.pack_into("<iii", data, 64, 2, 0, 0)
    data[76:192] = b"data\\chr023".ljust(116, b"\0")
    first = 64 + 128 + 4
    struct.pack_into("<iiI", data, first, 3, 3, 0)
    data[first + 12 : first + 76] = b"a.txt".ljust(64, b"\0")
    second = first + 80
    struct.pack_into("<iiI", data, second, 4, 4, 3)
    data[second + 12 : second + 76] = b"b.txt".ljust(64, b"\0")
    path.write_bytes(data)


class RepackArchiveTests(unittest.TestCase):
    def test_rebuild_updates_sizes_offsets_and_archive_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "source.idx"
            archive = root / "source.arc"
            replacement = root / "replacement.txt"
            make_index(index, archive.name)
            archive.write_bytes(b"AAABBBB")
            replacement.write_bytes(b"12345")

            out_index = root / "rebuilt.idx"
            out_archive = root / "rebuilt.arc"
            rebuild(
                index,
                out_index,
                out_archive,
                {"data/chr023/a.txt": replacement},
            )

            archive_name, entries = parse_index(out_index)
            self.assertEqual(archive_name, "rebuilt.arc")
            self.assertEqual(out_archive.read_bytes(), b"12345BBBB")
            self.assertEqual(entries[0].stored_size, 5)
            self.assertEqual(entries[1].offset, 5)
            self.assertEqual(struct.unpack_from("<I", out_index.read_bytes(), 8)[0], 9)


if __name__ == "__main__":
    unittest.main()
