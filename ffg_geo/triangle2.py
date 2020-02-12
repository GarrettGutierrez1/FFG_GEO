# -*- coding: utf-8 -*-
"""triangle.py

A module implementing Triangle2, which is the representation of a 2-dimensional triangle produced by triangulation.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

from typing import Iterable, List


class Triangle2(object):
    """A 2-dimensional triangle.

    Attributes:
        v: The vertices in counter-clockwise order.
        n: The neighbors in counter-clockwise order."""
    def __init__(self, v: Iterable = (None, None, None), n: Iterable = (None, None, None)) -> None:
        """Initializes the Triangle2.

        Args:
            v: The vertex indices.
            n: The neighbor triangle indices."""
        self.v = list(v[:3])  # type: List[int]
        self.n = list(n[:3])  # type: List[int]

    def __str__(self) -> str:
        """str's the triangle.

        Returns:
            The triangle as a str."""
        return 'Triangle: v: {} n: {}'.format(tuple(self.v), tuple(self.n))
