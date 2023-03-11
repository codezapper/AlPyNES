from interrupts import nmi, irq
from utils import check_bit


class RAM:
    def __init__(self, prg_rom, vram):
        self.data = [0] * 0xFFFF
        self.data[0x8000: (0x8000 + len(prg_rom))] = prg_rom
        self.data[0xC000: (0xC000 + len(prg_rom))] = prg_rom
        self._interrupt = -1
        self.vram = vram

    def write(self, address, value):
        if (address == 0x2007):
            vaddress = self.read(0x2006)
            self.write(0x2006, 1 + check_bit(self.read(0x2000)) * 31)
            self.vram.write(vaddress, value)
        else:
            self.data[address] = value

    def read(self, address):
        if (address == 0x2007):
            vaddress = self.read(0x2006)
            self.write(0x2006, 1 + check_bit(self.read(0x2000)) * 31)
            return self.vram.read(vaddress)
        return self.data[address]

    @property
    def interrupt(self):
        return self._interrupt

    @interrupt.setter
    def interrupt(self, value):
        self._interrupt = value
