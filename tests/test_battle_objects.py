from __future__ import annotations

import struct
import sys
from dataclasses import replace
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from battle_objects import (  # noqa: E402
    EXIST_NO_ATTACK_HANTEI,
    OBJECT_COUNT_OFFSET,
    OBJECT_POINTERS_OFFSET,
    OBJECT_READ_SIZE,
    parse_battle_object,
    projectile_judgment_by_owner,
    read_battle_objects,
)


class FakeProcess:
    def __init__(self, reads: dict[tuple[int, int], bytes]) -> None:
        self.reads = reads

    def read(self, address: int, size: int) -> bytes | None:
        return self.reads.get((address, size))


def object_data(*, owner: int = 0, object_type: int = 2, attack: int = 1,
                exist: int = 0, active: int = 1) -> bytes:
    data = bytearray(OBJECT_READ_SIZE)
    data[0x04] = owner
    struct.pack_into("<I", data, 0x0C, object_type)
    struct.pack_into("<I", data, 0x84, exist)
    struct.pack_into("<I", data, 0x64C, attack)
    struct.pack_into("<I", data, 0x7BC, active)
    return bytes(data)


class BattleObjectTests(unittest.TestCase):
    def test_projectile_judgment_requires_all_runtime_gates(self) -> None:
        active = replace(
            parse_battle_object(3, 0x5000, object_data(owner=1)),
            frame_attack_data_pointer=1,
        )
        disabled = replace(
            parse_battle_object(
                3, 0x5000, object_data(exist=EXIST_NO_ATTACK_HANTEI)
            ),
            frame_attack_data_pointer=1,
        )
        visual_only = parse_battle_object(3, 0x5000, object_data(attack=0))
        body_object = parse_battle_object(3, 0x5000, object_data(object_type=1))

        self.assertTrue(active.has_projectile_judgment)
        self.assertEqual(active.owner, 1)
        self.assertFalse(disabled.has_projectile_judgment)
        self.assertFalse(visual_only.has_projectile_judgment)
        self.assertFalse(body_object.has_projectile_judgment)

        p1 = replace(active, owner=0)
        p2 = replace(active, owner=1)
        self.assertEqual(projectile_judgment_by_owner([p1]), (True, False))
        self.assertEqual(projectile_judgment_by_owner([p1, p2]), (True, True))

    def test_reader_uses_native_pointer_table_and_skips_null_entries(self) -> None:
        base = 0x400000
        pointer = 0x5000
        animation = 0x6000
        raw_object = bytearray(object_data(owner=1))
        struct.pack_into("<I", raw_object, 0x648, animation)
        process = FakeProcess(
            {
                (base + OBJECT_COUNT_OFFSET, 4): struct.pack("<I", 2),
                (base + OBJECT_POINTERS_OFFSET, 8): struct.pack("<II", 0, pointer),
                (pointer, OBJECT_READ_SIZE): bytes(raw_object),
                (animation + 0x110, 4): struct.pack("<I", 0x7000),
            }
        )

        objects = read_battle_objects(process, base)

        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].table_index, 1)
        self.assertEqual(objects[0].address, pointer)
        self.assertEqual(objects[0].frame_attack_data_pointer, 0x7000)
        self.assertTrue(objects[0].has_projectile_judgment)


if __name__ == "__main__":
    unittest.main()
