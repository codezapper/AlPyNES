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

    def __init__(self, _ram):
        self.RAM = [0] * 0xFFFF
        self.RAM[0x8000: (0x8000 + len(_ram))] = _ram
        self.RAM[0xC000: (0xC000 + len(_ram))] = _ram
        self.SP = 0xFD
        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = (self.RAM[0xFFFD] << 8) | self.RAM[0xFFFC]
        self.PS = 0x24

    def ADC(first, second, addr_mode)
    def AND(first, second, addr_mode)
    def ASL(first, second, addr_mode)
    def BCC(first, second, addr_mode)
    def BCS(first, second, addr_mode)
    def BEQ(first, second, addr_mode)
    def BIT(first, second, addr_mode)
    def BMI(first, second, addr_mode)
    def BNE(first, second, addr_mode)
    def BPL(first, second, addr_mode)
    def BRK(first, second, addr_mode)
    def BVC(first, second, addr_mode)
    def BVS(first, second, addr_mode)
    def CLC(first, second, addr_mode)
    def CLD(first, second, addr_mode)
    def CLI(first, second, addr_mode)
    def CLV(first, second, addr_mode)
    def CMP(first, second, addr_mode)
    def CPX(first, second, addr_mode)
    def CPY(first, second, addr_mode)
    def DEC(first, second, addr_mode)
    def DEX(first, second, addr_mode)
    def DEY(first, second, addr_mode)
    def EOR(first, second, addr_mode)
    def INC(first, second, addr_mode)
    def INX(first, second, addr_mode)
    def INY(first, second, addr_mode)
    def JMP(first, second, addr_mode)
    def JSR(first, second, addr_mode)
    def LDA(first, second, addr_mode)
    def LDX(first, second, addr_mode)
    def LDY(first, second, addr_mode)
    def LSR(first, second, addr_mode)
    def NOP(first, second, addr_mode)
    def ORA(first, second, addr_mode)
    def PHA(first, second, addr_mode)
    def PHP(first, second, addr_mode)
    def PLA(first, second, addr_mode)
    def PLP(first, second, addr_mode)
    def ROL(first, second, addr_mode)
    def ROR(first, second, addr_mode)
    def RTI(first, second, addr_mode)
    def RTS(first, second, addr_mode)
    def SBC(first, second, addr_mode)
    def SEC(first, second, addr_mode)
    def SED(first, second, addr_mode)
    def SEI(first, second, addr_mode)
    def STA(first, second, addr_mode)
    def STX(first, second, addr_mode)
    def STY(first, second, addr_mode)
    def TAX(first, second, addr_mode)
    def TAY(first, second, addr_mode)
    def TSX(first, second, addr_mode)
    def TXA(first, second, addr_mode)
    def TXS(first, second, addr_mode)
    def TYA(first, second, addr_mode)

    def ALR(first, second, addr_mode)
    def ANC(first, second, addr_mode)
    def ARR(first, second, addr_mode)
    def ASL(first, second, addr_mode)
    def AXA(first, second, addr_mode)
    def AXS(first, second, addr_mode)
    def DCP(first, second, addr_mode)
    def ISC(first, second, addr_mode)
    def KIL(first, second, addr_mode)
    def LAS(first, second, addr_mode)
    def LAX(first, second, addr_mode)
    def OAL(first, second, addr_mode)
    def RLA(first, second, addr_mode)
    def RRA(first, second, addr_mode)
    def SAX(first, second, addr_mode)
    def SLO(first, second, addr_mode)
    def SRE(first, second, addr_mode)
    def SHX(first, second, addr_mode)
    def SHY(first, second, addr_mode)
    def TAS(first, second, addr_mode)
    def XAA(first, second, addr_mode)

    def NMI();
    def IRQ();
