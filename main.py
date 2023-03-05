import sys
import pygame
from rom import ROM
from cpu import CPU
from ppu import PPU

WIDTH = 256
HEIGHT = 240

RAM = [0] * 0xFFFF

try:
    r = ROM(sys.argv[1])
except Exception:
    print("Cannot open file")
    exit()

RAM[0x8000: (0x8000 + len(r.prg_rom))] = r.prg_rom
RAM[0xC000: (0xC000 + len(r.prg_rom))] = r.prg_rom

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

cpu = CPU(RAM)
ppu = PPU(RAM, r.chr_rom, screen)

while cpu.PC > 0:
    ppu.clock(1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
