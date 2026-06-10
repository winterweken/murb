"""Elementwise vector arithmetic on plain lists — the numpy-array stand-in.

Physics modules do `scalar * array`, `array + array`, `array ** 2` etc. on
monthly (12-element) series. Vec keeps that code unchanged without numpy.
"""


class Vec(list):
    @classmethod
    def zeros(cls, n):
        return cls([0.0] * n)

    def _zip(self, other, op):
        if isinstance(other, (list, tuple)):
            if len(other) != len(self):
                raise ValueError('Vec length mismatch: %d vs %d' % (len(self), len(other)))
            return Vec([op(a, b) for a, b in zip(self, other)])
        return Vec([op(a, other) for a in self])

    def __add__(self, other):
        return self._zip(other, lambda a, b: a + b)

    __radd__ = __add__

    def __sub__(self, other):
        return self._zip(other, lambda a, b: a - b)

    def __rsub__(self, other):
        return self._zip(other, lambda a, b: b - a)

    def __mul__(self, other):
        return self._zip(other, lambda a, b: a * b)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self._zip(other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return self._zip(other, lambda a, b: b / a)

    def __pow__(self, other):
        return self._zip(other, lambda a, b: a ** b)

    def __neg__(self):
        return Vec([-a for a in self])
