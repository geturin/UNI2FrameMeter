from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_32


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int


class Pe32:
    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe : pe + 4] != b"PE\0\0":
            raise ValueError("not a PE file")
        coff = pe + 4
        section_count = struct.unpack_from("<H", self.data, coff + 2)[0]
        optional_size = struct.unpack_from("<H", self.data, coff + 16)[0]
        optional = coff + 20
        if struct.unpack_from("<H", self.data, optional)[0] != 0x10B:
            raise ValueError("not PE32")
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        section_table = optional + optional_size
        sections = []
        for index in range(section_count):
            offset = section_table + index * 40
            name = self.data[offset : offset + 8].split(b"\0", 1)[0].decode("ascii")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            sections.append(
                Section(name, virtual_address, virtual_size, raw_offset, raw_size)
            )
        self.sections = sections

    def offset_to_va(self, offset: int) -> tuple[int, Section] | None:
        for section in self.sections:
            if section.raw_offset <= offset < section.raw_offset + section.raw_size:
                rva = section.virtual_address + offset - section.raw_offset
                return self.image_base + rva, section
        return None

    def va_to_offset(self, va: int) -> tuple[int, Section] | None:
        rva = va - self.image_base
        for section in self.sections:
            span = max(section.virtual_size, section.raw_size)
            if section.virtual_address <= rva < section.virtual_address + span:
                offset = section.raw_offset + rva - section.virtual_address
                return offset, section
        return None

    def absolute_xrefs(self, target_va: int) -> list[tuple[int, int, Section]]:
        needle = struct.pack("<I", target_va)
        results = []
        start = 0
        while True:
            offset = self.data.find(needle, start)
            if offset < 0:
                break
            mapped = self.offset_to_va(offset)
            if mapped is not None:
                va, section = mapped
                results.append((offset, va, section))
            start = offset + 1
        return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("offsets", nargs="+", help="module-relative offsets")
    parser.add_argument("--before", type=lambda value: int(value, 0), default=0x30)
    parser.add_argument("--after", type=lambda value: int(value, 0), default=0x30)
    args = parser.parse_args()

    pe = Pe32(args.exe)
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    for raw_offset in args.offsets:
        relative = int(raw_offset, 0)
        target_va = pe.image_base + relative
        xrefs = [item for item in pe.absolute_xrefs(target_va) if item[2].name == ".text"]
        print(f"\nTARGET uni2.exe+0x{relative:X} preferred=0x{target_va:08X} xrefs={len(xrefs)}")
        for file_offset, operand_va, section in xrefs:
            instruction_guess = operand_va - 6
            window_start_va = max(pe.image_base, instruction_guess - args.before)
            mapped = pe.va_to_offset(window_start_va)
            if mapped is None:
                continue
            window_offset, _ = mapped
            window_size = args.before + args.after + 16
            code = pe.data[window_offset : window_offset + window_size]
            print(f"\n  operand at 0x{operand_va:08X} (file+0x{file_offset:X})")
            for instruction in disassembler.disasm(code, window_start_va):
                marker = ">" if instruction.address <= operand_va < instruction.address + instruction.size else " "
                print(
                    f"  {marker} {instruction.address:08X}  "
                    f"{instruction.mnemonic:<8} {instruction.op_str}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
