class RAM:
    def __init__(self, prg_rom):
        self.data = [0] * 0xFFFF
        self.data[0x8000: (0x8000 + len(prg_rom))] = prg_rom
        self.data[0xC000: (0xC000 + len(prg_rom))] = prg_rom

    def write(self, address, value):
        self.data[address] = value

    def read(self, address):
        if ((address >= 0x2000) and (address <= 0x3FFF)):
            pass
            # return ppu_read(address)
        elif (address == 0x4016):
            pass
            # TODO : handle controller
            # if (poll_controller1 >= 0) {
            #     ret = readController1(poll_controller1++)
            #     if (poll_controller1 > 7) {
            #         poll_controller1 = -1
            #                 #     return ret | 0x40
            # }
            # return 0x40
        else:
            return self.data[address]
