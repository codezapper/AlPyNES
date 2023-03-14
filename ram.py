from interrupts import nmi, irq
from utils import check_bit


class RAM:
    def __init__(self, prg_rom, vram):
        self.data = [0] * 0xFFFF
        self.data[0x8000: (0x8000 + len(prg_rom))] = prg_rom
        self.data[0xC000: (0xC000 + len(prg_rom))] = prg_rom
        self._interrupt = -1
        self.vram = vram
        self._ppuaddr = 0
        self._latch_toggle = False

    def write(self, address, value):
        if (address == 0x2007):
            vaddress = self.ppuaddr
            self.vram.write(vaddress, value)
        elif (address == 0x2006):
            self.ppuaddr = value
        else:
            self.data[address] = value

    def read(self, address):
        if (address == 0x2007):
            vaddress = self.ppuaddr
            return self.vram.read(vaddress)
        return self.data[address]

    @property
    def ppuaddr(self):
        address = self._ppuaddr
        self._ppuaddr += 1 + check_bit(self.read(0x2000), 2) * 31

        return address

    @ppuaddr.setter
    def ppuaddr(self, value):
        if self._latch_toggle:
            self._ppuaddr <<= 8
            self._ppuaddr |= value
        else:
            self._ppuaddr = value
        self._latch_toggle = not self._latch_toggle

    @property
    def interrupt(self):
        return self._interrupt

    @interrupt.setter
    def interrupt(self, value):
        self._interrupt = value
