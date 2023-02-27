def check_bit(number, bit):
    if (number & (1 << bit)):
        return 1

    return 0

def set_bit(value, bit):
    return value | (1 << bit)

def clear_bit(value, bit):
    return value & ~(1 << bit)

