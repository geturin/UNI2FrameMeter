import struct
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cancel_state import read_chain_shift_state


class FakeReader:
    def __init__(self, memory: dict[tuple[int, int], bytes]):
        self.memory = memory

    def read(self, address: int, size: int) -> bytes | None:
        return self.memory.get((address, size))


class ChainShiftStateTests(unittest.TestCase):
    @staticmethod
    def entity(*, dynamic_flags: int = 0, timer: int = 0, animation: int = 0x1000) -> bytes:
        data = bytearray(0xBA4)
        struct.pack_into("<I", data, 0x480, dynamic_flags)
        struct.pack_into("<I", data, 0x48C, timer)
        struct.pack_into("<I", data, 0x648, animation)
        return bytes(data)

    def test_descriptor_bit_three_allows_chain_shift(self) -> None:
        reader = FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x2018, 1): b"\x08",
        })
        state = read_chain_shift_state(reader, self.entity())
        self.assertTrue(state.descriptor_allowed)
        self.assertTrue(state.allowed)

    def test_dynamic_bit_requires_active_timer(self) -> None:
        reader = FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x2018, 1): b"\x00",
        })
        self.assertFalse(
            read_chain_shift_state(
                reader, self.entity(dynamic_flags=2, timer=0)
            ).allowed
        )
        self.assertTrue(
            read_chain_shift_state(
                reader, self.entity(dynamic_flags=2, timer=1)
            ).allowed
        )

    def test_failed_pointer_read_is_reported_without_false_positive(self) -> None:
        state = read_chain_shift_state(FakeReader({}), self.entity())
        self.assertEqual(state.read_error, "unreadable_descriptor_pointer")
        self.assertFalse(state.allowed)


if __name__ == "__main__":
    unittest.main()
