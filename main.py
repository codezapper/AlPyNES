import sys
import pygame
from rom import ROM
from cpu import CPU
from ppu import PPU
from ram import RAM
from vram import VRAM

WIDTH = 256
HEIGHT = 240

try:
    r = ROM(sys.argv[1])
except Exception:
    print("Cannot open file")
    exit()

sram = RAM(r.prg_rom)
svram = VRAM(r.chr_rom)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

cpu = CPU(sram)

ppu = PPU(sram, svram, screen)

while cpu.PC > 0:
    cpu.clock()
    ppu.clock(1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
