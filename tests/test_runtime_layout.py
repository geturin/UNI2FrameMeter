from pathlib import Path
import struct
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from runtime_layout import (  # noqa: E402
    ENTITY_COUNT,
    ENTITY_STRIDE,
    RuntimeLayout,
    locate_battle_tick,
    locate_entity_pool,
    locate_object_table,
    validate_runtime_layout,
)


IMAGE_BASE = 0x400000
IMAGE_SIZE = 0x4000000


class FakeProcess:
    def __init__(self, reads: dict[tuple[int, int], bytes]) -> None:
        self.reads = reads

    def read(self, address: int, size: int) -> bytes | None:
        return self.reads.get((address, size))


class RuntimeLayoutTests(unittest.TestCase):
    def test_locates_tick_from_initializer_and_mode_checks(self) -> None:
        first = IMAGE_BASE + 0x596B2C
        code = bytearray()
        code += b"\xC7\x05" + struct.pack("<I", first) + b"\0\0\0\0"
        code += b"\xC7\x05" + struct.pack("<I", first + 4) + b"\x01\0\0\0"
        code += b"\xC7\x05" + struct.pack("<I", first + 8) + b"\0\0\0\0"
        code += b"\xC7\x05" + struct.pack("<I", IMAGE_BASE + 0x1234) + b"\0\0\0\0"
        code += b"\x83\xF8\x0C\x74\x12\x83\xF8\x0F\x74\x0D"
        self.assertEqual(
            locate_battle_tick(bytes(code), IMAGE_BASE, IMAGE_SIZE),
            0x596B34,
        )

    def test_entity_pool_uses_dominant_stride_reference(self) -> None:
        pool = IMAGE_BASE + 0xC34E80
        other = IMAGE_BASE + 0xC352B8
        prefix = b"\x69\xC0\xA4\x0B\0\0\x05"
        code = (
            prefix + struct.pack("<I", pool) + b"\x90"
            + prefix + struct.pack("<I", pool) + b"\x90"
            + prefix + struct.pack("<I", pool) + b"\x90"
            + prefix + struct.pack("<I", other)
        )
        self.assertEqual(locate_entity_pool(code, IMAGE_BASE, IMAGE_SIZE), 0xC34E80)

    def test_locates_adjacent_object_count_and_pointer_table(self) -> None:
        count = IMAGE_BASE + 0x858BA0
        pointers = count + 4
        code = (
            b"\x8B\x15" + struct.pack("<I", count)
            + b"\x56\x8B\xF1\x8B\x06\x3B\xD0\x7D\x14\x7E\x12\x8B\x0C\x85"
            + struct.pack("<I", pointers)
            + b"\x40\x89\x06\x85\xC9\x75"
        )
        self.assertEqual(
            locate_object_table(code, IMAGE_BASE, IMAGE_SIZE),
            (0x858BA0, 0x858BA4),
        )

    def test_runtime_validation_accepts_readable_sane_structures(self) -> None:
        module = 0x400000
        layout = RuntimeLayout(0x100, 0x200, 0x300, 0x304)
        pool = bytearray(ENTITY_STRIDE * ENTITY_COUNT)
        struct.pack_into("<I", pool, 0x7BC, 1)
        pool[0x438] = 0
        process = FakeProcess(
            {
                (module + 0x100, 4): struct.pack("<I", 123),
                (module + 0x200, len(pool)): bytes(pool),
                (module + 0x300, 4): struct.pack("<I", 2),
            }
        )
        validate_runtime_layout(process, module, layout)

    def test_public_readers_do_not_gate_on_a_whole_file_hash(self) -> None:
        for name in ("uni2_overlay.py", "uni2_frame_reader.py"):
            text = (ROOT / "src" / name).read_text(encoding="utf-8")
            self.assertNotIn("EXPECTED_SHA256", text)
            self.assertNotIn("SHA-256 does not match", text)


if __name__ == "__main__":
    unittest.main()
