# -*- coding: utf-8 -*-
"""vector2.py

Representation of a vector in 2D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import math


class Vector2(object):
    def __init__(self, x: float, y: float) -> None:
        self.__c = (x, y)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return self.plus(other)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return self.minus(other)

    def __mul__(self, other: float) -> 'Vector2':
        return self.times(other)

    def __truediv__(self, other: float) -> 'Vector2':
        return self.divide(other)

    def __getitem__(self, item: int) -> float:
        return self.__c[item]

    @property
    def x(self) -> float:
        return self.__c[0]

    @property
    def y(self) -> float:
        return self.__c[1]

    def clone(self) -> 'Vector2':
        return Vector2(self.__c[0], self.__c[1])

    def negated(self) -> 'Vector2':
        return Vector2(-self.__c[0], -self.__c[1])

    def plus(self, a: 'Vector2') -> 'Vector2':
        return Vector2(self.__c[0] + a.__c[0], self.__c[1] + a.__c[1])

    def minus(self, a: 'Vector2') -> 'Vector2':
        return Vector2(self.__c[0] - a.__c[0], self.__c[1] - a.__c[1])

    def times(self, a: float) -> 'Vector2':
        return Vector2(self.__c[0] * a, self.__c[1] * a)

    def divide(self, a: float) -> 'Vector2':
        return Vector2(self.__c[0] / a, self.__c[1] / a)

    def dot(self, a: 'Vector2') -> float:
        return self.__c[0] * a.__c[0] + self.__c[1] * a.__c[1]

    def lerp(self, a: 'Vector2', t: float) -> 'Vector2':
        return self.plus(a.minus(self).times(t))

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def distance(self, other: 'Vector2') -> float:
        return self.minus(other).length()

    def unit(self) -> 'Vector2':
        return self.divide(self.length())

    def angle(self, a: 'Vector2') -> float:
        return math.acos(self.unit().dot(a.unit()))

    def projection(self, a: 'Vector2') -> 'Vector2':
        return self.times(a.dot(self))

    def equivalent(self, other: 'Vector2', epsilon: float = 0.000001) -> bool:
        if self.distance(other) < epsilon:
            return True
        return False

    def rotated(self, rad: float) -> 'Vector2':
        x = self.__c[0] * math.cos(rad) - self.__c[1] * math.sin(rad)
        y = self.__c[0] * math.sin(rad) - self.__c[1] * math.cos(rad)
        return Vector2(x, y)
