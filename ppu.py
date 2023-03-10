import pygame
from pygame import Color
from pygame.surfarray import pixels2d
from utils import check_bit, set_bit, clear_bit



WIDTH = 256
HEIGHT = 240

CYCLES_PER_LINE = 341
OAMSIZE = 64*4

HIGH = 1
LOW = 0

BG_ENABLE = 3
SPRITES_ENABLE = 4

BG_TILE_SELECT = 4
FG_TILE_SELECT = 3

SPRITE_ZERO_BIT = 6
VBLANK_BIT = 7

FLIP_HORIZONTAL = 6
FLIP_VERTICAL = 7

IS_SPRITE = 1
IS_BACKGROUND = 0

NMI_INT = 0
IRQ_INT = 1

# VRAM:
# $0000-$0FFF	$1000	Pattern table 0
# $1000-$1FFF	$1000	Pattern table 1
# $2000-$23FF	$0400	Nametable 0
# $2400-$27FF	$0400	Nametable 1
# $2800-$2BFF	$0400	Nametable 2
# $2C00-$2FFF	$0400	Nametable 3
# $3000-$3EFF	$0F00	Mirrors of $2000-$2EFF
# $3F00-$3F1F	$0020	Palette RAM indexes
# $3F20-$3FFF	$00E0	Mirrors of $3F00-$3F1F

# OAM:
# $00, $04, $08, $0C	Sprite Y coordinate
# $01, $05, $09, $0D	Sprite tile #
# $02, $06, $0A, $0E	Sprite attribute
# $03, $07, $0B, $0F	Sprite X coordinate


# $0000-1FFF is normally mapped by the cartridge to a CHR-ROM or CHR-RAM, often with a bank switching mechanism.
# $2000-2FFF is normally mapped to the 2kB NES internal VRAM, providing 2 nametables with a mirroring configuration controlled by the cartridge, but it can be partly or fully remapped to RAM on the cartridge, allowing up to 4 simultaneous nametables.
# $3000-3EFF is usually a mirror of the 2kB region from $2000-2EFF. The PPU does not render from this address range, so this space has negligible utility.
# $3F00-3FFF is not configurable, always mapped to the internal palette control.


# PPUCTRL	$2000	VPHB SINN	NMI enable (V), PPU master/slave (P), sprite height (H), background tile select (B), sprite tile select (S), increment mode (I), nametable select (NN)
# PPUMASK	$2001	BGRs bMmG	color emphasis (BGR), sprite enable (s), background enable (b), sprite left column enable (M), background left column enable (m), greyscale (G)
# PPUSTATUS	$2002	VSO- ----	vblank (V), sprite 0 hit (S), sprite overflow (O); read resets write pair for $2005/$2006
# OAMADDR	$2003	aaaa aaaa	OAM read/write address
# OAMDATA	$2004	dddd dddd	OAM data read/write
# PPUSCROLL	$2005	xxxx xxxx	fine scroll position (two writes: X scroll, Y scroll)
# PPUADDR	$2006	aaaa aaaa	PPU read/write address (two writes: most significant byte, least significant byte)
# PPUDATA	$2007	dddd dddd	PPU data read/write
# OAMDMA	$4014	aaaa aaaa	OAM DMA high address

import sys

class PPU:
    def __init__(self, ram, vram, screen):
        self.ram = ram
        self.vram = vram
        self.v = 0
        self.t = 0
        self.fine_x = 0
        self.toggle = 0

        self.ppuctrl = 0x80
        self.ppumask = 0
        self._ppustatus = 0x0
        self.oamaddr = 0
        self.oamdata = [0] * OAMSIZE
        self.ppudata = 0
        self.oamdma = 0

        self.ppudata_buffer = 0

        self.base_offset = WIDTH * 4
        self.x_scroll = 0
        self.y_scroll = 0
        self.current_scanline = -1
        self.current_cycle = 0
        self.current_frame = 0
        self.screen = screen
        self.c = 0
        self.vram.update_palette()
        self.patterns = []
        self.attributes = [0] * 1024
        self.load_patterns()
        self.load_attributes()

    def load_patterns(self):
        for address_range in [[0x0000, 0x0FFF, 16], [0x1000, 0x1FFF, 16]]:
            tiles = []
            for i in range(*address_range):
                tile = []
                plane0 = []
                plane1 = []
                start = i
                end = i + 8
                for j in range(start, end):
                    plane0.append(self.vram.read(j))
                
                start = i + 8
                end = i + 16
                for j in range(start, end):
                    plane1.append(self.vram.read(j))

                for k in range(8):
                    combined = []
                    for b in range(8):
                        combined.append(check_bit(plane0[k], b) | (check_bit(plane1[k], b) << 1))
                    tile.append(combined[::-1])
                tiles.append(tile)
            self.patterns.append(tiles)

    def load_attributes(self):
        current_index = 0
        for index, start_at in enumerate([0x23C0, 0x27C0, 0x2BC0, 0x2FC0]):
            self.attributes[index] = [0] * 1024
            for i in range(64):
                current_byte = self.vram.read(start_at + i)
                self.attributes[index][current_index + 33] = current_byte >> 6
                self.attributes[index][current_index + 32] = (current_byte & 0b00110000) >> 4
                self.attributes[index][current_index + 1] = (current_byte & 0b00001100) >> 2
                self.attributes[index][current_index] = current_byte & 0b00000011
                current_index += 2

    def show_tile(self, bank, tile_no, start_x, start_y):
        for y, row in enumerate(self.patterns[bank][tile_no]):
            for x, col in enumerate(row):
                if col != 0:
                    self.screen.set_at((start_x+x, start_y+y), Color((255, 255, 255)))
        start_x += 8
        if x >= WIDTH:
            start_y += 8
            start_x = 0

    def clock(self, cpu_cycles):
        # if self.current_scanline == -1:
        #     self.ppustatus =  set_bit(self._ppustatus, VBLANK_BIT)
        # self.current_scanline += 1

        self.load_attributes()
        self.show_tile(1, 10, 100, 100)
        pygame.display.flip()

        # self.screen.set_at((50, 50), Color(255, 255, 255))
        # pygame.display.flip()
        # self.ppustatus = set_bit(self.ppustatus, VBLANK_BIT)
        # self.ram.interrupt = NMI_INT

        # pxarray = pygame.surfarray.pixels2d(self.screen)
        # for i in range(len(framebuffer)):
        #     framebuffer[i] = [128] * 240

        # for row in range(256):
        #     for col in range(128):
        #         # adr = (r / 8 * 0x100) + (r % 8) + (col / 8) * 0x10
        #         # pixel = ((self.vram.read(adr) >> (7-(col % 8))) & 1) + ((self.vram.read(adr + 8) >> (7-(col % 8))) & 1) * 2
        #         pxarray[row][col] = Color(128, 128, 128)
                # pxarray[(row * 128 * 3) + (col * 3) + 1] = 128
                # pxarray[(row * 128 * 3) + (col * 3) + 2] = 128
        # pxarray[100, 100] = Color(0, 255, 0)
        # pygame.display.flip()


    @property
    def ppuctrl(self):
        return self.ram.read(0x2000)
    
    @ppuctrl.setter
    def ppuctrl(self, value):
        self.ram.write(0x2000, value)

    @property
    def ppumask(self):
        return self.ram.read(0x2001)

    @ppumask.setter
    def ppumask(self, value):
        self.ram.write(0x2001, value)

    @property
    def ppustatus(self):
        self._ppustatus = self.ram.read(0x2002)
        self._ppustatus = clear_bit(self.ppustatus, VBLANK_BIT)
        # TODO: reset the address latch used by PPUSCROLL and PPUADDR
        return self._ppustatus

    @ppustatus.setter
    def ppustatus(self, value):
        self._ppustatus = value
        self.ram.write(0x2002, value)
        if (check_bit(self._ppustatus, VBLANK_BIT)) and (value & VBLANK_BIT):
            self.ram.interrupt = NMI_INT

    @property
    def oamaddr(self):
        return self.ram.read(0x2003)

    @oamaddr.setter
    def oamaddr(self, value):
        self.ram.write(0x2003, value)

    @property
    def oamdata(self):
        return self.ram.read(0x2004)

    @oamdata.setter
    def oamdata(self, value):
        self.ram.write(0x2004, value)

    @property
    def ppuscroll(self):
        return self.ram.read(0x2005)

    @ppuscroll.setter
    def ppuscroll(self, value):
        self.ram.write(0x2005, value)

    @property
    def ppuaddr(self):
        return self.ram.read(0x2006)

    @ppuaddr.setter
    def ppuaddr(self, value):
        self.ram.write(0x2006, value)

    @property
    def ppudata(self):
        return self.ram.read(0x2007)

    @ppudata.setter
    def ppudata(self, value):
        self.ram.write(0x2007, value)

    @property
    def oamdma(self):
        return self.ram.read(0x4014)

    @oamdma.setter
    def oamdma(self, value):
        self.ram.write(0x4014, value)
