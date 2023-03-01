from collections import namedtuple
from utils import check_bit, clear_bit, set_bit


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
INDEXED = 0
INDIRECT = 1
INDIRECTX = 2
INDIRECTY = 3

INVALID_IMMEDIATE = -32768


OP_MAPPING = [
    ["BRK", IMPLICIT, 1, 7], ["ORA", INDIRECTX, 2, 6], ["KIL", IMPLICIT, 1, 1], ["SLO", INDIRECTX, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["ORA", ZEROPAGE, 2, 5], ["ASL", ZEROPAGE, 2, 5], ["SLO", ZEROPAGE, 2, 5], ["PHP", IMPLICIT, 1, 3], ["ORA", IMMEDIATE, 2, 2],
    ["ASL", ACCUMULATOR, 1, 2], ["ANC", IMMEDIATE, 2, 2], ["NOP", INDIRECT, 3, 1], ["ORA", ABSOLUTE, 3, 4], ["ASL", ABSOLUTE, 3, 6], ["SLO", ABSOLUTE, 3, 6], ["BPL", RELATIVE, 2, 2], ["ORA", INDIRECTY, 2, -5], ["KIL", IMPLICIT, 1, 1], ["SLO", INDIRECTY, 2, 8],
    ["NOP", ABSOLUTEX, 2, 1], ["ORA", ZEROPAGEX, 2, 4], ["ASL", ZEROPAGEX, 2, 6], ["SLO", ZEROPAGEX, 2, 6], ["CLC", IMPLICIT, 1, 2], ["ORA", ABSOLUTEY, 3, -4], ["NOP", IMPLICIT, 1, 1], ["SLO", ABSOLUTEY, 3, 7], ["NOP", INDIRECT, 3, 1], ["ORA", ABSOLUTEX, 3, -4],
    ["ASL", ABSOLUTEX, 3, 7], ["SLO", ABSOLUTEX, 3, 7], ["JSR", ABSOLUTE, 3, 6], ["AND", INDIRECTX, 2, 6], ["KIL", IMPLICIT, 1, 1], ["RLA", INDIRECTX, 2, 8], ["BIT", ZEROPAGE, 2, 3], ["AND", ZEROPAGE, 2, 3], ["ROL", ZEROPAGE, 2, 5], ["RLA", ZEROPAGE, 2, 5],
    ["PLP", IMPLICIT, 1, 4], ["AND", IMMEDIATE, 2, 2], ["ROL", ACCUMULATOR, 1, 2], ["ANC", IMMEDIATE, 2, 2], ["BIT", ABSOLUTE, 3, 4], ["AND", ABSOLUTE, 3, 4], ["ROL", ABSOLUTE, 3, 6], ["RLA", ABSOLUTE, 3, 6], ["BMI", RELATIVE, 2, 2], ["AND", INDIRECTY, 2, -5],
    # 50
    ["KIL", IMPLICIT, 1, 1], ["RLA", INDIRECTY, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["AND", ZEROPAGEX, 2, 4], ["ROL", ZEROPAGEX, 2, 6], ["RLA", ZEROPAGEX, 2, 6], ["SEC", IMPLICIT, 1, 2], ["AND", ABSOLUTEY, 3, -4], ["NOP", IMPLICIT, 1, 1], ["RLA", ABSOLUTEY, 3, 7],
    ["NOP", INDIRECT, 3, 1], ["AND", ABSOLUTEX, 3, -4], ["ROL", ABSOLUTEX, 3, 7], ["RLA", ABSOLUTEX, 3, 7], ["RTI", IMPLICIT, 1, 6], ["EOR", INDIRECTX, 2, 6], ["KIL", IMPLICIT, 1, 1], ["SRE", INDIRECTX, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["EOR", ZEROPAGE, 2, 3],
    ["LSR", ZEROPAGE, 2, 5], ["SRE", ZEROPAGE, 2, 5], ["PHA", IMPLICIT, 1, 3], ["EOR", IMMEDIATE, 2, 2], ["LSR", ACCUMULATOR, 1, 2], ["ALR", IMMEDIATE, 2, 2], ["JMP", ABSOLUTE, 3, 3], ["EOR", ABSOLUTE, 3, 4], ["LSR", ABSOLUTE, 3, 6], ["SRE", ABSOLUTE, 3, 6],

    ["BVC", RELATIVE, 2, 2], ["EOR", INDIRECTY, 2, -5], ["KIL", IMPLICIT, 1, 1], ["SRE", INDIRECTY, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["EOR", ZEROPAGEX, 2, 4], ["LSR", ZEROPAGEX, 2, 6], ["SRE", ZEROPAGEX, 2, 6], ["CLI", IMPLICIT, 1, 2], ["EOR", ABSOLUTEY, 3, -4],
    ["NOP", IMPLICIT, 1, 1], ["SRE", ABSOLUTEY, 3, 7], ["NOP", INDIRECT, 3, 1], ["EOR", ABSOLUTEX, 3, -4], ["LSR", ABSOLUTEX, 3, 7], ["SRE", ABSOLUTEX, 3, 7], ["RTS", IMPLICIT, 1, 6], ["ADC", INDIRECTX, 2, 6], ["KIL", IMPLICIT, 1, 1], ["RRA", INDIRECTX, 2, 8],
    # 100
    ["NOP", ABSOLUTEX, 2, 1], ["ADC", ZEROPAGE, 2, 3], ["ROR", ZEROPAGE, 2, 5], ["RRA", ZEROPAGE, 2, 5], ["PLA", IMPLICIT, 1, 4], ["ADC", IMMEDIATE, 2, 2], ["ROR", ACCUMULATOR, 1, 2], ["ARR", IMMEDIATE, 2, 2], ["JMP", INDIRECT, 3, 5], ["ADC", ABSOLUTE, 3, 4],
    ["ROR", ABSOLUTE, 3, 6], ["RRA", ABSOLUTE, 3, 6], ["BVS", RELATIVE, 2, 2], ["ADC", INDIRECTY, 2, -5], ["KIL", IMPLICIT, 1, 1], ["RRA", INDIRECTY, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["ADC", ZEROPAGEX, 2, 4], ["ROR", ZEROPAGEX, 2, 6], ["RRA", ZEROPAGEX, 2, 6],
    ["SEI", IMPLICIT, 1, 2], ["ADC", ABSOLUTEY, 3, -4], ["NOP", IMPLICIT, 1, 1], ["RRA", ABSOLUTEY, 3, 7], ["NOP", INDIRECT, 3, 1], ["ADC", ABSOLUTEX, 3, -4], ["ROR", ABSOLUTEX, 3, 7], ["RRA", ABSOLUTEX, 3, 7], ["NOP", ZEROPAGEX, 2, 1], ["STA", INDIRECTX, 2, 6],
    ["NOP", IMMEDIATE, 2, 2], ["SAX", INDIRECTX, 2, 6], ["STY", ZEROPAGE, 2, 3], ["STA", ZEROPAGE, 2, 3], ["STX", ZEROPAGE, 2, 3], ["SAX", ZEROPAGE, 2, 3], ["DEY", IMPLICIT, 1, 2], ["NOP", IMMEDIATE, 2, 2], ["TXA", IMPLICIT, 1, 2], ["XAA", IMMEDIATE, 2, 2],
    ["STY", ABSOLUTE, 3, 4], ["STA", ABSOLUTE, 3, 4], ["STX", ABSOLUTE, 3, 4], ["SAX", ABSOLUTE, 3, 4], ["BCC", RELATIVE, 2, 2], ["STA", INDIRECTY, 2, 6], ["KIL", IMPLICIT, 1, 1], ["AXA", INDIRECTY, 2, 6], ["STY", ZEROPAGEX, 2, 4], ["STA", ZEROPAGEX, 2, 4],
    # 150
    ["STX", ZEROPAGEY, 2, 4], ["SAX", ZEROPAGEY, 2, 4], ["TYA", IMPLICIT, 1, 2], ["STA", ABSOLUTEY, 3, 5], ["TXS", IMPLICIT, 1, 2], ["TAS", ABSOLUTEY, 3, 5], ["SHY", ABSOLUTEX, 3, 5], ["STA", ABSOLUTEX, 3, 5], ["SHX", ABSOLUTEY, 3, 5], ["AXA", ABSOLUTEY, 3, 5],
    ["LDY", IMMEDIATE, 2, 2], ["LDA", INDIRECTX, 2, 6], ["LDX", IMMEDIATE, 2, 2], ["LAX", INDIRECTX, 2, 6], ["LDY", ZEROPAGE, 2, 3], ["LDA", ZEROPAGE, 2, 3], ["LDX", ZEROPAGE, 2, 3], ["LAX", ZEROPAGE, 2, 3], ["TAY", IMPLICIT, 1, 2], ["LDA", IMMEDIATE, 2, 2],
    ["TAX", IMPLICIT, 1, 2], ["OAL", IMMEDIATE, 2, 2], ["LDY", ABSOLUTE, 3, 4], ["LDA", ABSOLUTE, 3, 4], ["LDX", ABSOLUTE, 3, 4], ["LAX", ABSOLUTE, 3, 4], ["BCS", RELATIVE, 2, 2], ["LDA", INDIRECTY, 2, -5], ["KIL", IMPLICIT, 1, 1], ["LAX", INDIRECTY, 2, -5],
    ["LDY", ZEROPAGEX, 2, 4], ["LDA", ZEROPAGEX, 2, 4], ["LDX", ZEROPAGEY, 2, 4], ["LAX", ZEROPAGEY, 2, 4], ["CLV", IMPLICIT, 1, 2], ["LDA", ABSOLUTEY, 3, -4], ["TSX", IMPLICIT, 1, 2], ["LAS", ABSOLUTEY, 3, -4], ["LDY", ABSOLUTEX, 3, -4], ["LDA", ABSOLUTEX, 3, -4],
    ["LDX", ABSOLUTEY, 3, -4], ["LAX", ABSOLUTEY, 3, -4], ["CPY", IMMEDIATE, 2, 2], ["CMP", INDIRECTX, 2, 6], ["NOP", IMMEDIATE, 2, 2], ["DCP", INDIRECTX, 2, 8], ["CPY", ZEROPAGE, 2, 3], ["CMP", ZEROPAGE, 2, 3], ["DEC", ZEROPAGE, 2, 5], ["DCP", ZEROPAGE, 2, 5],
    # 200
    ["INY", IMPLICIT, 1, 2], ["CMP", IMMEDIATE, 2, 2], ["DEX", IMPLICIT, 1, 2], ["AXS", IMMEDIATE, 2, 2], ["CPY", ABSOLUTE, 3, 4], ["CMP", ABSOLUTE, 3, 4], ["DEC", ABSOLUTE, 3, 6], ["DCP", ABSOLUTE, 3, 6], ["BNE", RELATIVE, 2, 2], ["CMP", INDIRECTY, 2, -5],
    ["KIL", IMPLICIT, 1, 1], ["DCP", INDIRECTY, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["CMP", ZEROPAGEX, 2, 4], ["DEC", ZEROPAGEX, 2, 6], ["DCP", ZEROPAGEX, 2, 6], ["CLD", IMPLICIT, 1, 2], ["CMP", ABSOLUTEY, 3, -4], ["NOP", IMPLICIT, 1, 1], ["DCP", ABSOLUTEY, 3, 7],
    ["NOP", INDIRECT, 3, 1], ["CMP", ABSOLUTEX, 3, -4], ["DEC", ABSOLUTEX, 3, 7], ["DCP", ABSOLUTEX, 3, 7], ["CPX", IMMEDIATE, 2, 2], ["SBC", INDIRECTX, 2, 6], ["NOP", IMMEDIATE, 2, 2], ["ISC", INDIRECTX, 2, 8], ["CPX", ZEROPAGE, 2, 3], ["SBC", ZEROPAGE, 2, 3],
    ["INC", ZEROPAGE, 2, 5], ["ISC", ZEROPAGE, 2, 5], ["INX", IMPLICIT, 1, 2], ["SBC", IMMEDIATE, 2, 2], ["NOP", IMPLICIT, 1, 2], ["SBC", IMMEDIATE, 2, 2], ["CPX", ABSOLUTE, 3, 4], ["SBC", ABSOLUTE, 3, 4], ["INC", ABSOLUTE, 3, 6], ["ISC", ABSOLUTE, 3, 6],
    ["BEQ", RELATIVE, 2, 2], ["SBC", INDIRECTY, 2, -5], ["KIL", IMPLICIT, 1, 1], ["ISC", INDIRECTY, 2, 8], ["NOP", ABSOLUTEX, 2, 1], ["SBC", ZEROPAGEX, 2, 4], ["INC", ZEROPAGEX, 2, 6], ["ISC", ZEROPAGEX, 2, 6], ["SED", IMPLICIT, 1, 2], ["SBC", ABSOLUTEY, 3, -4],
    # 250
    ["NOP", IMPLICIT, 1, 1], ["ISC", ABSOLUTEY, 3, 7], ["NOP", INDIRECT, 3, 1], ["SBC", ABSOLUTEX, 3, -4], ["INC", ABSOLUTEX, 3, 7], ["ISC", ABSOLUTEX, 3, 7]
]

OP = namedtuple("op", ["name", "mode", "byte_size", "cycles"])


class CPU:
    NMI_INT = 1
    IRQ_INT = 2
    CF = 0
    ZF = 1
    ID = 2
    DM = 3
    B4 = 4
    B5 = 5
    OF = 6
    NF = 7

    def __init__(self, RAM):
        self.RAM = RAM
        self.SP = 0xFD
        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = 0xC000
        # self.PC = (self.RAM[0xFFFD] << 8) | self.RAM[0xFFFC]
        # import pdb pdb.set_trace()
        self.PS = 0x24

    def log_clock(self, opcode_id, first, second):
        opcode = OP(*OP_MAPPING[opcode_id])

        logline = "0x{:04X}  {:02X} {:02X} {:02X}  {:03s}{:28s}A:{:02X} X:{:02X} Y:{:02X} P:{:02X} SP:{:02X}".format(
            self.PC,
            opcode_id,
            first,
            second,
            opcode.name,
            "",
            self.A,
            self.X,
            self.Y,
            self.PS,
            self.SP
        )

        print(logline)

    def stack_push(self, value):
        self.RAM[self.SP + 0x100] = value
        self.SP -= 1

    def stack_pop(self):
        self.SP += 1
        value = self.RAM[self.SP + 0x100]
        return value

    def push_PC(self):
        high = self.PC >> 8
        low = (self.PC << 8) >> 8

        self.stack_push(high)
        self.stack_push(low)

    def pop_PC(self):
        low = self.stack_pop()
        high = self.stack_pop()

        PC = high
        PC <<= 8
        PC |= low

    def resolve_address(self, first, second, addr_mode):
        high = 0
        low = 0
        address = 0

        if addr_mode == ACCUMULATOR:
            return self.A
        if addr_mode == IMMEDIATE:
            return first
        if addr_mode == RELATIVE:
            return first
        if addr_mode == ZEROPAGE:
            return first % 256
        if addr_mode == ZEROPAGEX:
            return (first + self.X) % 256
        if addr_mode == ZEROPAGEY:
            return (first + self.Y) % 256
        if addr_mode == ABSOLUTE:
            address = first
            address = (second << 8) |address
            return address
        if addr_mode == ABSOLUTEX:
            address = first
            address = (second << 8) |address
            return address + self.X
        if addr_mode == ABSOLUTEY:
            address = first
            address = (second << 8) |address
            return address + self.Y
        if addr_mode == INDIRECTX:
            return (self.RAM[(first + self.X + 1) & 0xFF] << 8) | self.RAM[(first + self.X) & 0xFF]
        if addr_mode == INDIRECTY:
            high = self.RAM[(first + 1) & 0xFF] << 8
            low = self.RAM[first & 0xFF]
            return (high | low) + Y
        if addr_mode == INDIRECT:
            if (first == 0xFF):
                high = (second << 8)
                low = (second << 8) | 0x00FF
                address = (self.RAM[high] << 8) | self.RAM[low]
            else:
                high = second
                high <<= 8
                low = first
                address = (self.RAM[(high | low) + 1] << 8) | self.RAM[(high | low)]

            return address


    def is_jump(self, opcode):
        if opcode.name in {"BRK", "JMP", "JSR", "RTI"}:
            return True
        return False

    def clock(self):
        opcode_id = self.RAM[self.PC]
        opcode = OP(*OP_MAPPING[opcode_id])
    
        if (opcode.cycles == 0):
            self.PC += 1
            return 0

        first = (self.RAM[self.PC + 1])
        second = (self.RAM[self.PC + 2])

        self.log_clock(opcode_id, first, second)

        getattr(self, opcode.name)(first, second, opcode.mode)

        if (not self.is_jump(opcode)) and (self.PC > 0):
            self.PC += opcode.byte_size

        return opcode.cycles


    def write(self, first, second, addr_mode, value):
        if (ACCUMULATOR == addr_mode):
            self.A = value
        else:
            address = self.resolve_address(first, second, addr_mode)
            if (((address >= 0x2000) and (address <= 0x3FFF)) or (address == 0x4014)):
                pass
                #ppu_write(address, value)
            elif (address == 0x4016):
                pass
                #poll_controller1 = value
            else:
                self.RAM[address] = value


    def read(self, first, second, addr_mode):
        value = self.resolve_address(first, second, addr_mode)

        if addr_mode in [ACCUMULATOR, IMMEDIATE, RELATIVE]:
            return value
    
        if addr_mode in [ ZEROPAGE, ZEROPAGEX, ZEROPAGEY, ABSOLUTE, ABSOLUTEX, ABSOLUTEY, INDIRECTX, INDIRECTY, INDIRECT ]:
            if ((value >= 0) and (value <= 0x1FFF)):
                value &= 0x07FF

            if ((value >= 0x2000) and (value <= 0x3FFF)):
                pass
                # return ppu_read(value)
            elif (value == 0x4016):
                pass
                # TODO : handle controller
                # if (poll_controller1 >= 0) {
                #     ret = readController1(poll_controller1++)
                #     if (poll_controller1 > 7) {
                #         poll_controller1 = -1
                #     }
                #     return ret | 0x40
                # }
                # return 0x40
            else:
                # TODO: Do not read RAM directly, but use a separate function to support mappers
                return self.RAM[value]

    def ADC(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        self.PS = clear_bit(self.PS, self.OF)

        value = self.read(first, second, addr_mode) & 0xFF
        result = self.A + value + check_bit(self.PS, self.CF)

        self.PS = clear_bit(self.PS, self.CF)

        if ((~(self.A ^ value) & (self.A ^ result) & 0x80) > 0):
            self.PS = set_bit(self.PS, self.OF)

        if (0 == (result & 0xFF)):
            self.PS = set_bit(self.PS, self.ZF)
        if (check_bit(result, 7)):
            self.PS = set_bit(self.PS, self.NF)

        if (result > 255):
            self.PS = set_bit(self.PS, self.CF)

        self.A = result & 0xFF

    def AND(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        self.A &= self.read(first, second, addr_mode)
        if (0 == self.A):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.A, 7)):
            self.PS = set_bit(self.PS, self.NF)

    def ASL(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.CF)
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        value = self.read(first, second, addr_mode) & 0xFF

        if (check_bit(value, 7) == 1):
            self.PS = set_bit(self.PS, self.CF)

        value <<= 1        
        if (0 == value):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(value, 7)):
            self.PS = set_bit(self.PS, self.NF)

        self.write(first, second, addr_mode, value)

    def BCC(self, first, second, addr_mode):
        if (check_bit(self.PS, self.CF) == 0):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BCS(self, first, second, addr_mode):
        if (check_bit(self.PS, self.CF) == 1):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BEQ(self, first, second, addr_mode):
        if (check_bit(self.PS, self.ZF) == 1):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BIT(self, first, second, addr_mode):
        # if self.PC == 0xc782:
        #     import pdb; pdb.set_trace()
        value = self.read(first, second, addr_mode)
        result = self.A & value

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        self.PS = clear_bit(self.PS, self.OF)

        if (0 == result):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(value, 7)):
            self.PS = set_bit(self.PS, self.NF)

        if (check_bit(value, 6)):
            self.PS = set_bit(self.PS, self.OF)

    def BMI(self, first, second, addr_mode):
        if (check_bit(self.PS, self.NF) == 1):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BNE(self, first, second, addr_mode):
        if (check_bit(self.PS, self.ZF) == 0):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BPL(self, first, second, addr_mode):
        if (check_bit(self.PS, self.NF) == 0):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BRK(self, first, second, addr_mode):
        self.PC += 2
        self.push_PC()
        self.PC -= 2
        self.PHP(first, second, addr_mode)
        self.SEI(first, second, addr_mode)
        self.PC = (self.RAM[0xFFFF] << 8) | self.RAM[0xFFFE]

    def BVC(self, first, second, addr_mode):
        if (check_bit(self.PS, self.OF) == 0):
            self.PC += self.resolve_address(first, second, addr_mode)

    def BVS(self, first, second, addr_mode):
        if (check_bit(self.PS, self.OF) == 1):
            self.PC += self.resolve_address(first, second, addr_mode)

    def CLC(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.CF)

    def CLD(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.DM)

    def CLI(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.ID)

    def CLV(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.OF)

    def CMP(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.CF)
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        value = self.read(first, second, addr_mode) & 0xFF

        if (self.A >= value):
            self.PS = set_bit(self.PS, self.CF)

        if (self.A == value):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.A-value, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def CPX(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.CF)
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        value = self.read(first, second, addr_mode) & 0xFF

        if (self.X >= value):
            self.PS = set_bit(self.PS, self.CF)

        if (self.X == value):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.X-value, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def CPY(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.CF)
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        value = self.read(first, second, addr_mode) & 0xFF

        if (self.Y >= value):
            self.PS = set_bit(self.PS, self.CF)

        if (self.Y == value):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.Y-value, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def DEC(self, first, second, addr_mode):
        value = (self.read(first, second, addr_mode) & 0xFF) - 1

        self.write(first, second, addr_mode, value)

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.read(first, second, addr_mode)):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(value, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def DEX(self, first, second, addr_mode):
        self.X -= 1

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.X):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.X, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def DEY(self, first, second, addr_mode):
        self.Y -= 1

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.Y):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.Y, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def EOR(self, first, second, addr_mode):
        self.A ^= self.read(first, second, addr_mode)

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.A):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.A, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def INC(self, first, second, addr_mode):
        value = self.read(first, second, addr_mode) + 1

        self.write(first, second, addr_mode, value)

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == value):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(value, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def INX(self, first, second, addr_mode):
        self.X += 1

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.X):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.X, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def INY(self, first, second, addr_mode):
        self.Y += 1

        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)
        if (0 == self.Y):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.Y, 7) == 1):
            self.PS = set_bit(self.PS, self.NF)

    def JMP(self, first, second, addr_mode):
        self.PC = self.resolve_address(first, second, addr_mode)

    def JSR(self, first, second, addr_mode):
        self.PC += 2
        self.push_PC()
        self.PC = self.resolve_address(first, second, addr_mode)

    def LDA(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        self.A = self.read(first, second, addr_mode)
        if (self.A == 0x7C):
            # Only for debugging
            pass

        if (0 == self.A):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.A, 7)):
            self.PS = set_bit(self.PS, self.NF)

    def LDX(self, first, second, addr_mode):
        self.PS = clear_bit(self.PS, self.ZF)
        self.PS = clear_bit(self.PS, self.NF)

        self.X  = self.read(first, second, addr_mode)
        if (0 == self.X):
            self.PS = set_bit(self.PS, self.ZF)

        if (check_bit(self.X, 7)):
            self.PS = set_bit(self.PS, self.NF)

    def LDY(self, first, second, addr_mode):
        pass

    def LSR(self, first, second, addr_mode):
        pass

    def NOP(self, first, second, addr_mode):
        pass

    def ORA(self, first, second, addr_mode):
        pass

    def PHA(self, first, second, addr_mode):
        pass

    def PHP(self, first, second, addr_mode):
        pass

    def PLA(self, first, second, addr_mode):
        pass

    def PLP(self, first, second, addr_mode):
        pass

    def ROL(self, first, second, addr_mode):
        pass

    def ROR(self, first, second, addr_mode):
        pass

    def RTI(self, first, second, addr_mode):
        pass

    def RTS(self, first, second, addr_mode):
        pass

    def SBC(self, first, second, addr_mode):
        pass

    def SEC(self, first, second, addr_mode):
        self.PS = set_bit(self.PS, self.CF)

    def SED(self, first, second, addr_mode):
        pass

    def SEI(self, first, second, addr_mode):
        pass

    def STA(self, first, second, addr_mode):
        self.write(first, second, addr_mode, self.A)

    def STX(self, first, second, addr_mode):
        self.write(first, second, addr_mode, self.X)

    def STY(self, first, second, addr_mode):
        self.write(first, second, addr_mode, self.Y)

    def TAX(self, first, second, addr_mode):
        pass

    def TAY(self, first, second, addr_mode):
        pass

    def TSX(self, first, second, addr_mode):
        pass

    def TXA(self, first, second, addr_mode):
        pass

    def TXS(self, first, second, addr_mode):
        pass

    def TYA(self, first, second, addr_mode):
        pass


    def ALR(self, first, second, addr_mode):
        pass

    def ANC(self, first, second, addr_mode):
        pass

    def ARR(self, first, second, addr_mode):
        pass

    def ASL(self, first, second, addr_mode):
        pass

    def AXA(self, first, second, addr_mode):
        pass

    def AXS(self, first, second, addr_mode):
        pass

    def DCP(self, first, second, addr_mode):
        pass

    def ISC(self, first, second, addr_mode):
        pass

    def KIL(self, first, second, addr_mode):
        pass

    def LAS(self, first, second, addr_mode):
        pass

    def LAX(self, first, second, addr_mode):
        pass

    def OAL(self, first, second, addr_mode):
        pass

    def RLA(self, first, second, addr_mode):
        pass

    def RRA(self, first, second, addr_mode):
        pass

    def SAX(self, first, second, addr_mode):
        pass

    def SLO(self, first, second, addr_mode):
        pass

    def SRE(self, first, second, addr_mode):
        pass

    def SHX(self, first, second, addr_mode):
        pass

    def SHY(self, first, second, addr_mode):
        pass

    def TAS(self, first, second, addr_mode):
        pass

    def XAA(self, first, second, addr_mode):
        pass

    def NMI(self):
        pass

    def IRQ(self):
        pass
