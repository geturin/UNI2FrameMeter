from __future__ import annotations

from dataclasses import asdict, dataclass
import struct
from typing import Protocol

from runtime_layout import (
    OBJECT_SUMMARY_ADDRESS, OBJECT_SUMMARY_WORDS, ACTIVE_OFFSET,
    ANIMATION_OFFSET, ATTACK_OFFSET, DESCRIPTOR_OFFSET, MOVE_CODE_OFFSET,
    PARENT_POINTER_OFFSET, OBJECT_READ_SIZE,
)


# The native CreateObject/update/collision paths enumerate this pointer table.
# These are module-relative offsets for the pinned UNI2 executable.
OBJECT_COUNT_OFFSET = 0x87B4E0
OBJECT_POINTERS_OFFSET = 0x87B4E4
MAX_OBJECTS = 2000

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
    # animation frame, not object+0x658's cache.
    frame_attack_data_pointer: int | None
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
        parent_pointer=u32(data, PARENT_POINTER_OFFSET),
        descriptor_pointer=u32(data, DESCRIPTOR_OFFSET),
        animation_pointer=u32(data, ANIMATION_OFFSET),
        frame_attack_data_pointer=0,
        attack_data_pointer=u32(data, ATTACK_OFFSET),
        move_code=u32(data, MOVE_CODE_OFFSET),
        active_marker=data[ACTIVE_OFFSET],
    )


def read_battle_objects(
    process: MemoryReader,
    module_base: int,
    count_offset: int = OBJECT_COUNT_OFFSET,
    pointers_offset: int = OBJECT_POINTERS_OFFSET,
) -> list[BattleObject]:
    count_raw = process.read(module_base + count_offset, 4)
    if count_raw is None:
        raise RuntimeError("Native snapshot has no battle-object count")
    count = u32(count_raw, 0)
    if count > MAX_OBJECTS:
        raise RuntimeError("Native snapshot reports an invalid battle-object count")
    if not count:
        return []
    # The DLL copies a native summary for every non-null object, preserving
    # the real runtime fields and avoiding a 4 MiB whole-pool copy each tick.
    chunks = getattr(process, "chunks", ())
    summaries = [chunk for chunk in chunks if chunk.address == OBJECT_SUMMARY_ADDRESS]
    if len(summaries) != 1:
        raise RuntimeError("Native snapshot has no unique battle-object summary")
    summary_size = summaries[0].size
    row_bytes = OBJECT_SUMMARY_WORDS * 4
    if summary_size != row_bytes * count:
        raise RuntimeError("Native battle-object summary has invalid bounds")
    raw = process.read(OBJECT_SUMMARY_ADDRESS, summary_size)
    pointers = process.read(module_base + pointers_offset, count * 4)
    if raw is None or pointers is None:
        raise RuntimeError("Native battle-object summary or pointer table is incomplete")
    objects: list[BattleObject] = []
    seen: set[int] = set()
    for row in struct.iter_unpack("<12I", raw):
        index, address, owner, object_type, exist, parent, descriptor, animation, frame_attack, attack, move_code, active = row
        if index >= count or index in seen or address != u32(pointers, index * 4) or owner > 255 or active > 255:
            raise RuntimeError("Native battle-object summary does not match its pointer table")
        seen.add(index)
        if not address:
            if any(row[2:]):
                raise RuntimeError("Null native battle-object summary contains fabricated fields")
            continue
        objects.append(BattleObject(index, address, owner, object_type, exist, parent, descriptor, animation,
                                    None if frame_attack == 0xFFFFFFFF else frame_attack,
                                    attack, move_code, active))
    if len(seen) != count:
        raise RuntimeError("Native battle-object summary is missing live objects")
    return objects


def projectile_judgment_by_owner(
    objects: list[BattleObject],
) -> tuple[bool, bool]:
    result = [False, False]
    for item in objects:
        if item.owner in (0, 1) and item.has_projectile_judgment:
            result[item.owner] = True
    return result[0], result[1]
