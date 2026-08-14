from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Protocol


ENTITY_STRIDE = 0xBA4
ENTITY_COUNT = 12
MAX_OBJECTS = 256


class MemoryReader(Protocol):
    def read(self, address: int, size: int) -> bytes | None: ...


@dataclass(frozen=True)
class PeCode:
    image_base: int
    image_size: int
    text: bytes


@dataclass(frozen=True)
class RuntimeLayout:
    battle_tick_offset: int
    entity_pool_offset: int
    object_count_offset: int
    object_pointers_offset: int


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def read_pe_code(path: Path) -> PeCode:
    data = path.read_bytes()
    if len(data) < 0x100:
        raise RuntimeError("uni2.exe is too small to be a PE image")
    pe_offset = _u32(data, 0x3C)
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise RuntimeError("uni2.exe is not a PE image")
    coff = pe_offset + 4
    section_count = _u16(data, coff + 2)
    optional_size = _u16(data, coff + 16)
    optional = coff + 20
    if _u16(data, optional) != 0x10B:
        raise RuntimeError("only the 32-bit UNI2 executable is supported")
    image_base = _u32(data, optional + 28)
    image_size = _u32(data, optional + 56)
    section_table = optional + optional_size
    for index in range(section_count):
        section = section_table + index * 40
        name = data[section : section + 8].split(b"\0", 1)[0]
        if name != b".text":
            continue
        raw_size = _u32(data, section + 16)
        raw_offset = _u32(data, section + 20)
        text = data[raw_offset : raw_offset + raw_size]
        if len(text) != raw_size:
            raise RuntimeError("uni2.exe has a truncated .text section")
        return PeCode(image_base, image_size, text)
    raise RuntimeError("uni2.exe has no .text section")


def _absolute_to_rva(address: int, image_base: int, image_size: int) -> int:
    rva = address - image_base
    if not 0 <= rva < image_size:
        raise RuntimeError(f"signature resolved outside image: 0x{address:08X}")
    return rva


def locate_battle_tick(text: bytes, image_base: int, image_size: int) -> int:
    """Find BattleState fields initialized as 0, 1, 0 and used by mode checks."""
    candidates: set[int] = set()
    for offset in range(0, max(0, len(text) - 46)):
        if not (
            text[offset : offset + 2] == b"\xC7\x05"
            and text[offset + 6 : offset + 10] == b"\0\0\0\0"
            and text[offset + 10 : offset + 12] == b"\xC7\x05"
            and text[offset + 16 : offset + 20] == b"\x01\0\0\0"
            and text[offset + 20 : offset + 22] == b"\xC7\x05"
            and text[offset + 26 : offset + 30] == b"\0\0\0\0"
            and text[offset + 40 : offset + 43] == b"\x83\xF8\x0C"
            and text[offset + 45 : offset + 48] == b"\x83\xF8\x0F"
        ):
            continue
        first = _u32(text, offset + 2)
        second = _u32(text, offset + 12)
        tick = _u32(text, offset + 22)
        if second == first + 4 and tick == first + 8:
            candidates.add(tick)
    if len(candidates) != 1:
        raise RuntimeError(
            f"unable to uniquely locate battle tick ({len(candidates)} candidates)"
        )
    return _absolute_to_rva(candidates.pop(), image_base, image_size)


def locate_entity_pool(text: bytes, image_base: int, image_size: int) -> int:
    """Find the dominant absolute base in entity-index * 0xBA4 accesses."""
    prefixes = (
        b"\x69\xC0\xA4\x0B\x00\x00\x05",       # imul eax; add eax, base
        b"\x69\xC8\xA4\x0B\x00\x00\x81\xC1", # imul ecx; add ecx, base
    )
    counts: Counter[int] = Counter()
    for prefix in prefixes:
        start = 0
        while True:
            offset = text.find(prefix, start)
            if offset < 0:
                break
            operand = offset + len(prefix)
            if operand + 4 <= len(text):
                counts[_u32(text, operand)] += 1
            start = offset + 1
    if not counts:
        raise RuntimeError("unable to locate entity pool")
    ranked = counts.most_common(2)
    address, references = ranked[0]
    if references < 2 or (len(ranked) > 1 and ranked[1][1] == references):
        raise RuntimeError("entity-pool signature is ambiguous")
    return _absolute_to_rva(address, image_base, image_size)


def locate_object_table(
    text: bytes, image_base: int, image_size: int
) -> tuple[int, int]:
    """Find paired object-count and pointer-table operands in native iteration."""
    suffix = b"\x56\x8B\xF1\x8B\x06\x3B\xD0\x7D\x14\x7E\x12\x8B\x0C\x85"
    tail = b"\x40\x89\x06\x85\xC9\x75"
    candidates: set[tuple[int, int]] = set()
    start = 0
    while True:
        offset = text.find(b"\x8B\x15", start)
        if offset < 0:
            break
        if (
            text[offset + 6 : offset + 6 + len(suffix)] == suffix
            and text[offset + 6 + len(suffix) + 4 : offset + 6 + len(suffix) + 10]
            == tail
        ):
            count = _u32(text, offset + 2)
            pointers = _u32(text, offset + 6 + len(suffix))
            if pointers == count + 4:
                candidates.add((count, pointers))
        start = offset + 1
    if len(candidates) != 1:
        raise RuntimeError(
            f"unable to uniquely locate battle-object table ({len(candidates)} candidates)"
        )
    count, pointers = candidates.pop()
    return (
        _absolute_to_rva(count, image_base, image_size),
        _absolute_to_rva(pointers, image_base, image_size),
    )


def resolve_runtime_layout(path: Path) -> RuntimeLayout:
    pe = read_pe_code(path)
    count, pointers = locate_object_table(pe.text, pe.image_base, pe.image_size)
    return RuntimeLayout(
        battle_tick_offset=locate_battle_tick(pe.text, pe.image_base, pe.image_size),
        entity_pool_offset=locate_entity_pool(pe.text, pe.image_base, pe.image_size),
        object_count_offset=count,
        object_pointers_offset=pointers,
    )


def validate_runtime_layout(
    process: MemoryReader, module_base: int, layout: RuntimeLayout
) -> None:
    tick = process.read(module_base + layout.battle_tick_offset, 4)
    pool = process.read(
        module_base + layout.entity_pool_offset,
        ENTITY_STRIDE * ENTITY_COUNT,
    )
    count_raw = process.read(module_base + layout.object_count_offset, 4)
    if tick is None or pool is None or count_raw is None:
        raise RuntimeError("resolved UNI2 runtime layout is unreadable")
    if _u32(count_raw, 0) > MAX_OBJECTS:
        raise RuntimeError("resolved battle-object count is outside the valid range")
    for slot in range(ENTITY_COUNT):
        entity = pool[slot * ENTITY_STRIDE : (slot + 1) * ENTITY_STRIDE]
        if _u32(entity, 0x7BC):
            player = entity[0x438]
            if player not in (0, 1):
                raise RuntimeError("resolved entity pool failed its player-slot validation")
