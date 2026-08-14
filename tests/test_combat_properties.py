import struct
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from combat_properties import read_cancel_properties, read_invincibility_properties


class FakeReader:
    def __init__(self, memory: dict[tuple[int, int], bytes]):
        self.memory = memory

    def read(self, address: int, size: int) -> bytes | None:
        return self.memory.get((address, size))


class CombatPropertiesTests(unittest.TestCase):
    @staticmethod
    def entity() -> bytearray:
        data = bytearray(0xBA4)
        struct.pack_into("<I", data, 0x648, 0x1000)
        return data

    @staticmethod
    def cancel_reader(
        *, normal: int = 0, special: int = 0, actionable: int = 0,
        status1: int = 0,
    ) -> FakeReader:
        descriptor = bytearray(0x0F)
        descriptor[0x01] = normal
        descriptor[0x02] = special
        descriptor[0x04] = actionable
        struct.pack_into("<I", descriptor, 0x0B, status1)
        return FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x200D, 0x0F): bytes(descriptor),
        })

    def test_cancel_properties_are_recomputed_from_live_inputs(self) -> None:
        entity = self.entity()
        struct.pack_into("<I", entity, 0x1CC, 1)
        properties = read_cancel_properties(
            self.cancel_reader(normal=2, special=1, status1=1), bytes(entity)
        )
        self.assertEqual(
            properties.tokens(),
            ("normal_cancel", "special_cancel", "ex_cancel"),
        )

    def test_conditional_result_cache_is_ignored(self) -> None:
        entity = self.entity()
        entity[0x798:0x79E] = bytes((0, 1, 1, 1, 1, 1))
        properties = read_cancel_properties(self.cancel_reader(), bytes(entity))
        self.assertEqual(properties.tokens(), ())

    def test_hit_and_damage_rules_use_current_impact_flags(self) -> None:
        entity = self.entity()
        reader = self.cancel_reader(normal=1, special=3)
        struct.pack_into("<I", entity, 0x1CC, 1)
        contact = read_cancel_properties(reader, bytes(entity))
        self.assertTrue(contact.normal)
        self.assertFalse(contact.special)
        struct.pack_into("<I", entity, 0x1CC, 2)
        damage = read_cancel_properties(reader, bytes(entity))
        self.assertTrue(damage.normal)
        self.assertTrue(damage.special)

    def test_timed_override_replaces_non_ff_rules(self) -> None:
        entity = self.entity()
        struct.pack_into("<I", entity, 0x46C, 5)
        struct.pack_into("<I", entity, 0x460, 0x0000FF02)
        properties = read_cancel_properties(
            self.cancel_reader(normal=1, special=1), bytes(entity)
        )
        self.assertTrue(properties.normal)
        self.assertFalse(properties.special)
        self.assertEqual(properties.normal_rule, 2)
        self.assertEqual(properties.special_rule, 1)

    def test_native_actionable_shortcut_is_not_displayed(self) -> None:
        properties = read_cancel_properties(
            self.cancel_reader(normal=2, special=2, actionable=1),
            bytes(self.entity()),
        )
        self.assertTrue(properties.native_actionable)
        self.assertEqual(properties.tokens(), ())

    def test_cs_uses_live_descriptor_bit_not_conditional_cache(self) -> None:
        entity = self.entity()
        entity[0x79C] = 0
        properties = read_cancel_properties(
            self.cancel_reader(status1=0x08), bytes(entity)
        )
        self.assertTrue(properties.chain_shift)
        self.assertIn("cs_cancel", properties.tokens())

        entity[0x79C] = 1
        expired = read_cancel_properties(self.cancel_reader(), bytes(entity))
        self.assertFalse(expired.chain_shift)
        self.assertNotIn("cs_cancel", expired.tokens())

    def test_cs_timed_override_expires_on_the_current_frame(self) -> None:
        entity = self.entity()
        struct.pack_into("<I", entity, 0x480, 0x02)
        struct.pack_into("<I", entity, 0x48C, 1)
        active = read_cancel_properties(self.cancel_reader(), bytes(entity))
        self.assertTrue(active.chain_shift)

        struct.pack_into("<I", entity, 0x48C, 0)
        expired = read_cancel_properties(self.cancel_reader(), bytes(entity))
        self.assertFalse(expired.chain_shift)

    def test_attribute_filter_requires_active_timer(self) -> None:
        entity = self.entity()
        struct.pack_into("<I", entity, 0x4A0, 0x15F)
        reader = FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x200D, 1): b"\x00",
        })
        expired = read_invincibility_properties(reader, bytes(entity))
        self.assertFalse(expired.head)
        self.assertFalse(expired.throw)
        struct.pack_into("<I", entity, 0x4AC, 1)
        active = read_invincibility_properties(reader, bytes(entity))
        self.assertTrue(active.head)
        self.assertTrue(active.body)
        self.assertTrue(active.foot)
        self.assertTrue(active.light_foot)
        self.assertTrue(active.dive)
        self.assertTrue(active.projectile)
        self.assertTrue(active.throw)

    def test_descriptor_five_is_native_full_invincibility(self) -> None:
        reader = FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x200D, 1): b"\x05",
        })
        properties = read_invincibility_properties(reader, bytes(self.entity()))
        self.assertTrue(properties.strike)
        self.assertTrue(properties.throw)
        self.assertTrue(properties.full)

    def test_paired_system_timers_are_full_invincibility(self) -> None:
        entity = self.entity()
        entity[0x204] = 3
        entity[0x207] = 2
        reader = FakeReader({
            (0x110C, 4): struct.pack("<I", 0x2000),
            (0x200D, 1): b"\x00",
        })
        properties = read_invincibility_properties(reader, bytes(entity))
        self.assertEqual(properties.strike_timer, 3)
        self.assertEqual(properties.throw_timer, 2)
        self.assertTrue(properties.full)


if __name__ == "__main__":
    unittest.main()
