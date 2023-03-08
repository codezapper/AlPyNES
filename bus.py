# TODO Fix duplicated code

IMPLICIT = 0
ACCUMULATOR = 1
IMMEDIATE = 2
ZEROPAGE = 3
ZEROPAGEX = 4
ZEROPAGEY = 5
RELATIVE = 6
ABSOLUTE = 7
ABSOLUTEX = 8
ABSOLUTEY = 9
INDEXED = 10
INDIRECT = 11
INDIRECTX = 12
INDIRECTY = 13

INVALID_IMMEDIATE = -32768

class Bus:
    def __init__(self, RAM):
        self._RAM = RAM

    def resolve_address(self, first, second, addr_mode, A, X, Y):
        high = 0
        low = 0
        address = 0

        if addr_mode == ACCUMULATOR:
            return A
        if addr_mode == IMMEDIATE:
            return first
        if addr_mode == RELATIVE:
            if first > 127:
                return first - 256
            return first
        if addr_mode == ZEROPAGE:
            return first % 256
        if addr_mode == ZEROPAGEX:
            return (first + X) % 256
        if addr_mode == ZEROPAGEY:
            return (first + Y) % 256
        if addr_mode == ABSOLUTE:
            address = first
            address = (second << 8) |address
            return address & 0xFFFF
        if addr_mode == ABSOLUTEX:
            address = first
            address = (second << 8) |address
            return (address + X) & 0xFFFF
        if addr_mode == ABSOLUTEY:
            address = first
            address = (second << 8) |address
            return (address + Y) & 0xFFFF
        if addr_mode == INDIRECTX:
            return (self._RAM[(first + X + 1) & 0xFF] << 8) | self._RAM[(first + X) & 0xFF]
        if addr_mode == INDIRECTY:
            high = self._RAM[(first + 1) & 0xFF] << 8
            low = self._RAM[first & 0xFF]
            return ((high | low) + Y) & 0xFFFF
        if addr_mode == INDIRECT:
            if (first == 0xFF):
                high = (second << 8)
                low = (second << 8) | 0x00FF
                address = (self._RAM[high] << 8) | self._RAM[low]
            else:
                high = second
                high <<= 8
                low = first
                address = (self._RAM[(high | low) + 1] << 8) | self._RAM[(high | low)]

            return address & 0xFFFF

    def write(self, first, second, addr_mode, value, A, X, Y):
        address = self.resolve_address(first, second, addr_mode, A, X, Y)
        if (((address >= 0x2000) and (address <= 0x3FFF)) or (address == 0x4014)):
            pass
            #ppu_write(address, value)
        elif (address == 0x4016):
            pass
            #poll_controller1 = value
        else:
            self._RAM[address] = value

    def read(self, first, second, addr_mode, A, X, Y):
        address = self.resolve_address(first, second, addr_mode, A, X, Y)

        if addr_mode in [ACCUMULATOR, IMMEDIATE, RELATIVE]:
            return address
    
        if addr_mode in [ ZEROPAGE, ZEROPAGEX, ZEROPAGEY, ABSOLUTE, ABSOLUTEX, ABSOLUTEY, INDIRECTX, INDIRECTY, INDIRECT ]:
            if ((address >= 0) and (address <= 0x1FFF)):
                address &= 0x07FF

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
                return self._RAM[address]
