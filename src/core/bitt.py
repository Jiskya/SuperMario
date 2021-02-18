def nbits(n):
    return ~(~0b00 << n)

def check(x, MASK, y):
    return x & MASK == y

def carrayfrom(values, CARRY):
    for i in range(len(values)):
        v2[i] = v2[i] << CARRY
    return tuple(v2)

def carrayfrom_copy(values, CARRY):
    v2 = values.copy()
    for i in range(len(v2)):
        v2[i] = v2[i] << CARRY
    return tuple(v2)

def make(CARRY, n):
    v = []
    for i in range(n):
        v.append( i << CARRY )
    return tuple(v)

class BitTool:
    def __init__(self):
        self.adder = 0

    def bits_carry_mask(self, n):
        ret = (n, self.adder, nbits(n) << self.adder)
        self.adder += n
        return ret

