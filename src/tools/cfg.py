import math


def nbits(n):
    return ~(~0b00 << n)


class Configure:
    def __init__(self, max, carry, mask):
        self.__maxsize__, self.__carry__, self.__mask__ = max, carry, mask
        self.__size__ = 0

    def add(self, n):
        '''
            尽量这样使用:
                cmaker = CfgMaker()
                C.style  = cmaker.make(4) # 最多有4个style选项
                C.orient = cmaker.make(2) # 最多有2个orient选项
                C.style.normal, C.style.super = C.style.add(2)
        '''
        if self.__size__ + n > self.__maxsize__:
            raise Exception('超出设置选项最大限制')
        v = []
        for i in range(n):
            v.append(i + self.__size__ << self.__carry__)
        self.__size__ += n
        return tuple(v)

    def __call__(self, x, y):
        return (x & self.__mask__) == y

    def get_mask(self):
        return self.__mask__

    def get_carry(self):
        return self.__carry__

    def get_size(self):
        return self.__size__

    def get_max_size(self):
        return self.__maxsize__

class CfgMaker:
    def __init__(self):
        self._c_ = 0

    def make(self, maxsize):
        '''
            maxsize最好取 2 ** n
        '''
        ret = Configure(maxsize, self._c_, nbits(maxsize) << self._c_)
        self._c_ += math.ceil(math.log(maxsize, 2))
        return ret
