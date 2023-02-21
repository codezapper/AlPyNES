class ROM:
    def __init__(self, _filename):
        self._filename = _filename
        self._load()
    
    def _parse_header(self):
        header_dict = {}
        header_dict["header_constant"] = ""
        for i in range(4):
            header_dict["header_constant"] += chr(self.input_array[i])
        header_dict["prg_size"] = self.input_array[4]
        header_dict["chr_size"] = self.input_array[5]
        header_dict["flag6"] = self.input_array[6]
        header_dict["flag7"] = self.input_array[7]
        header_dict["flag8"] = self.input_array[8]
        header_dict["flag9"] = self.input_array[9]
        header_dict["flag10"] = self.input_array[10]
        header_dict["unused_padding"] = ""

        for i in range(5):
            header_dict["unused_padding"] += chr(self.input_array[11 + i])

        return header_dict

    def _load(self):
        if not self._filename:
            return
        
        try:
            with open(self._filename, "rb") as input_file:
                self.input_array = input_file.read()
                self.header = self._parse_header()
        except FileNotFoundError:
            return

        self.mirroring = self.header["flag6"] & 1
        self.has_prg_ram = self.header["flag6"] & 2
        self.has_trainer = self.header["flag6"] & 3
        self.ignore_mirroring_control = self.header["flag6"] & 4
        self.vs_unisystem = self.header["flag7"] & 1
        self.playchoice10 = self.header["flag7"] & 2
        self.is_nes20 = (((self.header["flag7"] & 3) | (self.header["flag7"] & 4)) == 2)
        self.prg_ram_size = self.header["flag8"]
        self.tv_system = self.header["flag9"] & 1  # 0: NTSC, 1: PAL

        self.mapper = self.header["flag7"] & 5 | \
                        self.header["flag7"] & 6 | \
                        self.header["flag7"] & 7 | \
                        self.header["flag7"] & 8
        self.mapper = self.mapper << 4

        self.mapper |= self.header["flag6"] & 5 | \
                        self.header["flag6"] & 6 | \
                        self.header["flag6"] & 7 | \
                        self.header["flag6"] & 8
        self.trainer = 0
        start_prg = 16

        if self.has_trainer:
            start_prg += 512
        end_prg = start_prg + (16384 * self.header["prg_size"])

        self.prg_rom = self.input_array[start_prg: end_prg]
        self.chr_rom = self.input_array[end_prg: (self.header["chr_size"] * 8192)]

