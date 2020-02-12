# -*- coding: utf-8 -*-
"""plane3.py

Representation of a directed plane in 3D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""


from .vector3 import Vector3


class Plane3(object):
    def __init__(self, normal: Vector3, w: float) -> None:
        self.__normal = normal
        self.__w = w

    @property
    def normal(self) -> Vector3:
        return self.__normal

    @property
    def w(self) -> float:
        return self.__w

    def clone(self) -> 'Plane3':
        return Plane3(self.__normal.clone(), self.__w)

    def flipped(self) -> 'Plane3':
        return Plane3(self.__normal.negated(), -self.__w)

    def distance(self, vector: Vector3) -> float:
        return self.__normal.dot(vector) - self.__w

    def coplanar(self, vector: Vector3, epsilon: float = 0.000001) -> bool:
        return self.distance(vector) < epsilon

    def equivalent(self, other: 'Plane3', epsilon: float = 0.000001) -> bool:
        return self.__normal.equivalent(other.__normal) and abs(self.__w - other.__w) < epsilon

    @staticmethod
    def from_points(a: Vector3, b: Vector3, c: Vector3) -> 'Plane3':
        normal = b.minus(a).cross(c.minus(a)).unit()
        return Plane3(normal, normal.dot(a))
