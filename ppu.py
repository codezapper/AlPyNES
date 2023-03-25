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
        self.current_tile = -1
        self.start_x = 0
        self.current_x = 0
        self.current_cycle = 0
        self.current_frame = 0
        self.screen = screen
        self.c = 0
        self.vram.update_palette()
        self.patterns = []
        self.framebuffer = pixels2d(self.screen)
        self.during_vblank = False
        self.attributes = [0] * 1024
        self.nametables = [0, 1, 2, 3]
        self.nametables[0] = [0] * 1024
        self.nametables[1] = [0] * 1024
        self.nametables[2] = [0] * 1024
        self.nametables[3] = [0] * 1024
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

    def show_tile(self, bank, tile_no):
        row = self.patterns[0][tile_no][self.current_scanline % 8]
        col = row[self.current_x]
        if col != 0:
            self.screen.set_at((self.start_x + self.current_x, self.current_scanline), Color((255, 255, 255)))

    def show_tile_pos(self, bank, tile_no, start_col, start_row, palette_address):
        start_x = start_col * 8
        start_y = start_row * 8

        block_x = int(start_col / 4)
        block_y = int(start_row / 4)

        attr_addr = int(block_y * 8) + block_x
        attr_byte = self.vram.read(palette_address + attr_addr)

        block_id = int(((start_col % 4) / 2) + (((start_row  % 4) / 2) * 2))
        which_palette = (attr_byte >> (block_id * 2)) & 0x03


        for y, row in enumerate(self.patterns[bank][tile_no]):
            for x, col in enumerate(row):
                    color = self.vram._PALETTE[self.vram.palette[which_palette][col]]
                    self.framebuffer[x + start_x][y + start_y] = Color([255, color[0], color[1], color[2]])

    def fetch_tile_no(self, nametable_id):
        base_address = 0x2000 + (nametable_id * 0x400)
        tile_address = base_address + self.current_scanline + self.current_x + self.start_x
        int(self.start_x / 8) + (self.current_scanline * 8)
        t = self.vram.read(tile_address)
        return self.vram.read(tile_address)

    def show_current_pixel(self, nametable_id):
        x = self.current_x
        y = self.current_scanline

        if x >= WIDTH or y >= HEIGHT:
            return

        tile_x = x % 8
        tile_y = y % 8

        nametable_address = 0x2000 + nametable_id * 0x400
        bg_bank = 1 if check_bit(self.ppuctrl, BG_TILE_SELECT) else 0
        palette_address = 0x27C0 - (0x400 * bg_bank)

        start_row = int(y / 30)
        start_col = int(x / 32)
        tile_no = self.vram.read(nametable_address + (start_row * 32) + start_col)

        start_x = int(x/4)
        start_y = int(y/4)

        block_x = int(start_col / 4)
        block_y = int(start_row / 4)

        attr_addr = int(block_y * 8) + block_x
        attr_byte = self.vram.read(palette_address + attr_addr)

        block_id = int(((start_col % 4) / 2) + (((start_row  % 4) / 2) * 2))
        which_palette = (attr_byte >> (block_id * 2)) & 0x03

        row = self.patterns[bg_bank][tile_no][tile_y]
        col = row[tile_x]
        color = self.vram._PALETTE[self.vram.palette[which_palette][col]]

        self.framebuffer[tile_x + start_x][tile_y + start_y] = Color([255, color[0], color[1], color[2]])

    def draw_background(self, nametable_id):
        nametable_address = 0x2000 + nametable_id * 0x400
        bank = 1 if check_bit(self.ppuctrl, BG_TILE_SELECT) else 0
        palette_address = 0x27C0 - (0x400 * bank)

        scanline = self.current_scanline
        start_row = int(scanline / 8)
        if start_row >= 30:
            return
        start_col = int(self.current_x / 8)

        # for start_col in range(32):
        # for start_row in range(30):
        tile_no = self.vram.read(nametable_address + (start_row * 32) + start_col)
        start_x = (self.current_x // 8) * 8
        start_y = (self.current_scanline // 8) * 8
        if ((scanline % 8) + start_y) >= HEIGHT:
            return

        block_x = int(start_col / 4)
        block_y = int(start_row / 4)

        attr_addr = int(block_y * 8) + block_x
        attr_byte = self.vram.read(palette_address + attr_addr)

        block_id = int(((start_col % 4) / 2) + (((start_row  % 4) / 2) * 2))
        which_palette = (attr_byte >> (block_id * 2)) & 0x03


        row = self.patterns[bank][tile_no][scanline % 8]
        col = row[self.current_x % 8]

        color = self.vram._PALETTE[self.vram.palette[which_palette][col]]
        # print(start_y, (scanline % 8))
        self.framebuffer[(self.current_x % 8) + start_x][(scanline % 8) + start_y] = Color([255, color[0], color[1], color[2]])

    def clock(self, cpu_cycles):
        nametable_id = (check_bit(self.ppuctrl, 1) << 1) | check_bit(self.ppuctrl, 0)
        self.current_cycle += 1
        self.current_x += 1
        # self.current_scanline += 1
        if self.current_x >= WIDTH:
            self.current_x = 0
            self.current_scanline += 1
        if (self.current_scanline == -1):
            # self.screen.fill((0,0,0))
            pygame.display.flip()
            self.ppustatus = clear_bit(self._ppustatus, VBLANK_BIT)
            self.ram.interrupt = -1
        elif 0 <= self.current_scanline <= 256:
            # pass
            self.draw_background(nametable_id)
        elif 241 <= self.current_scanline <= 260:
            self.ppustatus = set_bit(self._ppustatus, VBLANK_BIT)
            if (not self.during_vblank) and (self.ppuctrl & 0x80):
                self.ram.interrupt = NMI_INT
        elif self.current_scanline > 260:
            self.current_scanline = -1
                # self.draw_background(nametable_id)

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
    def oamdma(self):
        return self.ram.read(0x4014)

    @oamdma.setter
    def oamdma(self, value):
        self.ram.write(0x4014, value)
