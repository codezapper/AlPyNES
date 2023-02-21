import sys
from rom import ROM
from cpu import CPU

RAM = [0] * 0xFFFF

try:
    r = ROM(sys.argv[1])
except Exception:
    print("Cannot open file")
    exit()

RAM[0x8000: (0x8000 + len(r.prg_rom))] = r.prg_rom
RAM[0xC000: (0xC000 + len(r.prg_rom))] = r.prg_rom

cpu = CPU(RAM)

while cpu.PC > 0:
    cpu.clock()