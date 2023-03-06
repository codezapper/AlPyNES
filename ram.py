class RAM:
    def __init__(self, prg_rom):
        self.data = [0] * 0xFFFF
        self.data[0x8000: (0x8000 + len(prg_rom))] = prg_rom
        self.data[0xC000: (0xC000 + len(prg_rom))] = prg_rom
        self._interrupt = 0

    def write(self, address, value):
        self.data[address] = value

    def read(self, address):
        return self.data[address]

    @property
    def interrupt(self):
        return self._interrupt

    @interrupt.setter
    def interrupt(self, value):
        self._interrupt = value
