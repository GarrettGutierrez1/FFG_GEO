# -*- coding: utf-8 -*-
"""vector3.py

Representation of a vector in 3D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import math


class Vector3(object):
    def __init__(self, x: float, y: float, z: float) -> None:
        self.__c = (x, y, z)

    def __add__(self, other: 'Vector3') -> 'Vector3':
        return self.plus(other)

    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return self.minus(other)

    def __mul__(self, other: float) -> 'Vector3':
        return self.times(other)

    def __truediv__(self, other: float) -> 'Vector3':
        return self.divide(other)

    def __getitem__(self, item: int) -> float:
        return self.__c[item]

    @property
    def x(self) -> float:
        return self.__c[0]

    @property
    def y(self) -> float:
        return self.__c[1]

    @property
    def z(self) -> float:
        return self.__c[2]

    def clone(self) -> 'Vector3':
        return Vector3(self.__c[0], self.__c[1], self.__c[2])

    def negated(self) -> 'Vector3':
        return Vector3(-self.__c[0], -self.__c[1], -self.__c[2])

    def plus(self, a: 'Vector3') -> 'Vector3':
        return Vector3(self.__c[0] + a.__c[0], self.__c[1] + a.__c[1], self.__c[2] + a.__c[2])

    def minus(self, a: 'Vector3') -> 'Vector3':
        return Vector3(self.__c[0] - a.__c[0], self.__c[1] - a.__c[1], self.__c[2] - a.__c[2])

    def times(self, a: float) -> 'Vector3':
        return Vector3(self.__c[0] * a, self.__c[1] * a, self.__c[2] * a)

    def divide(self, a: float) -> 'Vector3':
        return Vector3(self.__c[0] / a, self.__c[1] / a, self.__c[2] / a)

    def dot(self, a: 'Vector3') -> float:
        return self.__c[0] * a.__c[0] + self.__c[1] * a.__c[1] + self.__c[2] * a.__c[2]

    def lerp(self, a: 'Vector3', t: float) -> 'Vector3':
        return self.plus(a.minus(self).times(t))

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def distance(self, other: 'Vector3') -> float:
        return self.minus(other).length()

    def unit(self) -> 'Vector3':
        return self.divide(self.length())

    def angle(self, a: 'Vector3') -> float:
        return math.acos(self.unit().dot(a.unit()))

    def projection(self, a: 'Vector3') -> 'Vector3':
        return self.times(a.dot(self))

    def equivalent(self, other: 'Vector3', epsilon: float = 0.000001) -> bool:
        return self.distance(other) < epsilon

    def cross(self, a: 'Vector3') -> 'Vector3':
        return Vector3(self.__c[1] * a.__c[2] - self.__c[2] * a.__c[1], self.__c[2] * a.__c[0] - self.__c[0] * a.__c[2],
                       self.__c[0] * a.__c[1] - self.__c[1] * a.__c[0])
