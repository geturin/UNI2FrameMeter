from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import struct
from typing import Protocol


# The native CreateObject/update/collision paths enumerate this pointer table.
# These are module-relative offsets for the pinned UNI2 executable.
OBJECT_COUNT_OFFSET = 0x858BA0
OBJECT_POINTERS_OFFSET = 0x858BA4
OBJECT_READ_SIZE = 0x7C0
MAX_OBJECTS = 256

OBJ_TYPE_FIREBALL = 0x2
EXIST_NO_ATTACK_HANTEI = 0x400


class MemoryReader(Protocol):
    def read(self, address: int, size: int) -> bytes | None: ...


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


@dataclass(frozen=True)
class BattleObject:
    table_index: int
    address: int
    owner: int
    object_type: int
    exist_flags: int
    parent_pointer: int
    descriptor_pointer: int
    animation_pointer: int
    # The collision path consumes the attack record stored on the current
    # animation frame, not object+0x64C's cache.
    frame_attack_data_pointer: int
    attack_data_pointer: int
    move_code: int
    active_marker: int

    @property
    def has_projectile_judgment(self) -> bool:
        return bool(
            self.active_marker
            and self.object_type == OBJ_TYPE_FIREBALL
            and self.frame_attack_data_pointer
            and not self.exist_flags & EXIST_NO_ATTACK_HANTEI
        )

    def debug_dict(self) -> dict[str, int | bool]:
        return {
            **asdict(self),
            "has_projectile_judgment": self.has_projectile_judgment,
        }


def parse_battle_object(table_index: int, address: int, data: bytes) -> BattleObject:
    if len(data) < OBJECT_READ_SIZE:
        raise ValueError("truncated battle object")
    return BattleObject(
        table_index=table_index,
        address=address,
        # CreateObject copies the creating entity's owner byte to object+0x04.
        owner=data[0x04],
        object_type=u32(data, 0x0C),
        exist_flags=u32(data, 0x84),
        parent_pointer=u32(data, 0x3F8),
        descriptor_pointer=u32(data, 0x644),
        animation_pointer=u32(data, 0x648),
        frame_attack_data_pointer=0,
        attack_data_pointer=u32(data, 0x64C),
        move_code=u32(data, 0x6AC),
        active_marker=u32(data, 0x7BC),
    )


def read_battle_objects(
    process: MemoryReader,
    module_base: int,
    count_offset: int = OBJECT_COUNT_OFFSET,
    pointers_offset: int = OBJECT_POINTERS_OFFSET,
) -> list[BattleObject]:
    count_raw = process.read(module_base + count_offset, 4)
    if count_raw is None:
        return []
    count = u32(count_raw, 0)
    if count > MAX_OBJECTS:
        return []
    if not count:
        return []
    pointers_raw = process.read(module_base + pointers_offset, count * 4)
    if pointers_raw is None:
        return []
    objects: list[BattleObject] = []
    for table_index, (address,) in enumerate(
        struct.iter_unpack("<I", pointers_raw)
    ):
        if not address:
            continue
        data = process.read(address, OBJECT_READ_SIZE)
        if data is None or len(data) < OBJECT_READ_SIZE:
            continue
        item = parse_battle_object(table_index, address, data)
        if item.animation_pointer:
            attack_raw = process.read(item.animation_pointer + 0x110, 4)
            if attack_raw is not None:
                item = replace(
                    item,
                    frame_attack_data_pointer=u32(attack_raw, 0),
                )
        objects.append(item)
    return objects


def projectile_judgment_by_owner(
    objects: list[BattleObject],
) -> tuple[bool, bool]:
    result = [False, False]
    for item in objects:
        if item.owner in (0, 1) and item.has_projectile_judgment:
            result[item.owner] = True
    return result[0], result[1]
