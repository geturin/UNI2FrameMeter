from __future__ import annotations

import argparse
from pathlib import Path
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_MEM


sys.path.insert(0, str(Path(__file__).resolve().parent))
from disassemble_xrefs import Pe32


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path)
    parser.add_argument("offsets", nargs="+", help="structure displacements")
    args = parser.parse_args()
    wanted = {int(value, 0) for value in args.offsets}
    pe = Pe32(args.exe)
    text = next(section for section in pe.sections if section.name == ".text")
    code = pe.data[text.raw_offset : text.raw_offset + text.raw_size]
    start_va = pe.image_base + text.virtual_address
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    disassembler.detail = True
    disassembler.skipdata = True
    matches: dict[int, list[tuple[int, str, str]]] = {value: [] for value in wanted}
    for instruction in disassembler.disasm(code, start_va):
        if instruction.id == 0:
            continue
        displacements = {
            operand.mem.disp
            for operand in instruction.operands
            if operand.type == X86_OP_MEM
        }
        for displacement in wanted.intersection(displacements):
            matches[displacement].append(
                (instruction.address - pe.image_base, instruction.mnemonic, instruction.op_str)
            )
    for displacement in sorted(wanted):
        rows = matches[displacement]
        print(f"\n## +0x{displacement:X} ({len(rows)} references)")
        for rva, mnemonic, operands in rows:
            print(f"0x{rva:08X}  {mnemonic:<8} {operands}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
