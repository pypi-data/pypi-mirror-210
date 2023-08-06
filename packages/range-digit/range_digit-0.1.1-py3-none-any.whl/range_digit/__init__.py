from copy import copy
from decimal import ROUND_HALF_UP, Decimal


def digits2str(digits):
    """List of digits to str"""
    return "".join(str(i) for i in digits)


def tuple2decimal(sign, digits, exponent):
    """Value of as_tuple to Decimal"""
    return Decimal(f"{'-' * sign}{digits2str(digits)}e{exponent}")


def change_digits(digits, num):
    """Change digits by num"""
    n = len(digits) - 1
    digits[n] += num
    while digits[n] < 0:
        while digits[n] < 0:
            digits[n] += 10
            digits[n - 1] -= 1
        n -= 1
    return digits


def overflow(digits):
    """Overflow digits"""
    p = 0
    lst = []
    for i in reversed(digits):
        p += i
        p, q = p // 10, p % 10
        lst.append(q)
    if p:
        lst.append(p)
    return list(reversed(lst))


class RangeDigit:
    def __init__(self, value, exact=False):
        sign, digits, exponent = Decimal(value).as_tuple()
        if exact or digits == (0,):
            sup = low = digits
        else:
            sup = list(digits) + [5]
            low = change_digits(sup.copy(), -10)
            if sign:
                low, sup = sup, low
            exponent -= 1
        self.low = tuple2decimal(sign, low, exponent)
        self.sup = tuple2decimal(sign, sup, exponent)

    def correct(self):
        if self.low > self.sup:
            self.low, self.sup = self.sup, self.low

    def __neg__(self):
        sd = copy(self)
        sd.low, sd.sup = -sd.sup, -sd.low
        return sd

    def __abs__(self):
        sd = copy(self)
        sd.low = abs(sd.low)
        sd.sup = abs(sd.sup)
        sd.correct()
        return sd

    def __iadd__(self, other):
        if isinstance(other, RangeDigit):
            self.low += other.low
            self.sup += other.sup
        else:
            self.low += other
            self.sup += other
        return self

    def __isub__(self, other):
        if isinstance(other, RangeDigit):
            self.low -= other.sup
            self.sup -= other.low
        else:
            self.low -= other
            self.sup -= other
        return self

    def __imul__(self, other):
        if isinstance(other, RangeDigit):
            if self.low.is_signed() == other.low.is_signed():
                self.low *= other.low
                self.sup *= other.sup
            else:
                self.low *= other.sup
                self.sup *= other.low
        else:
            self.low *= other
            self.sup *= other
        self.correct()
        return self

    def __itruediv__(self, other):
        if isinstance(other, RangeDigit):
            if self.low.is_signed() == other.low.is_signed():
                self.low /= other.sup
                self.sup /= other.low
            else:
                self.low /= other.low
                self.sup /= other.sup
        else:
            self.low /= other
            self.sup /= other
        self.correct()
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, RangeDigit):
            if self.low.is_signed() == other.low.is_signed():
                self.low //= other.sup
                self.sup //= other.low
            else:
                self.low //= other.low
                self.sup //= other.sup
        else:
            self.low //= other
            self.sup //= other
        self.correct()
        return self

    def __add__(self, other):
        sd = copy(self)
        sd += other
        return sd

    def __sub__(self, other):
        sd = copy(self)
        sd -= other
        return sd

    def __mul__(self, other):
        sd = copy(self)
        sd *= other
        return sd

    def __truediv__(self, other):
        sd = copy(self)
        sd /= other
        return sd

    def __floordiv__(self, other):
        sd = copy(self)
        sd //= other
        return sd

    def tostr(self):
        return f"<RangeDigit [{self.low} - {self.sup})>"

    def __repr__(self):
        if self.low.is_signed() != self.sup.is_signed():
            return self.tostr()
        if self.low == self.sup:
            return str(self.low)
        if self.low < 0:
            return "-" + repr(abs(self))
        sign, digits, exponent = self.sup.as_tuple()
        sup = tuple2decimal(sign, change_digits(list(digits), -1), exponent)
        sup = max(self.low, sup)
        num = max(self.low.as_tuple()[2], sup.as_tuple()[2])
        while True:
            d = Decimal(f"1e{num}")
            el = self.low.quantize(d, ROUND_HALF_UP)
            es = sup.quantize(d, ROUND_HALF_UP)
            if el == es:
                break
            num += 1
        return str(el)
