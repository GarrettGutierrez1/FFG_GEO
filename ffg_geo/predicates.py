# -*- coding: utf-8 -*-
"""predicates.py

A module wherein the vector sideness and in-circle predicates are implemented.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import enum

from ffg_geo.vector2 import Vector2


class Orientation(enum.Enum):
    """Orientation enum for usage in sideness predicate."""
    CO_LINEAR = 0
    LEFT = 1
    RIGHT = 2


class Position(enum.Enum):
    """Position enum for usage in the in-circle predicate."""
    ON = 0
    INSIDE = 1
    OUTSIDE = 2


def side(a: Vector2, b: Vector2, c: Vector2) -> Orientation:
    """Vector sideness predicate. Determines on which side c is of the line (a,b).

    Args:
        a: The source vector.
        b: The destination vector.
        c: The vector to determine sideness of w.r.t. (a,b).

    Returns:
        The orientation (left, right, or co-linear)."""
    area = ((b.x - a.x) * (c.y - a.y)) - ((c.x - a.x) * (b.y - a.y))
    if area > 0.0:
        return Orientation.LEFT
    if area < 0.0:
        return Orientation.RIGHT
    return Orientation.CO_LINEAR


def in_circle(a: Vector2, b: Vector2, c: Vector2, d: Vector2) -> Position:
    """Vector in-circle predicate. Determines d's position w.r.t the circle defined by (a,b,c). The points a, b, and c
    must be in counter-clockwise order or the opposite result will be returned.

    Args:
        a: Vector a in the circle defined by (a,b,c).
        b: Vector b in the circle defined by (a,b,c).
        c: Vector c in the circle defined by (a,b,c).
        d: Vector d to test the position of w.r.t. (a,b,c).

    Returns:
        The position (in-circle, out-circle, or on-circle).
    """
    adx = a.x - d.x
    ady = a.y - d.y
    bdx = b.x - d.x
    bdy = b.y - d.y
    cdx = c.x - d.x
    cdy = c.y - d.y
    abdet = adx * bdy - bdx * ady
    bcdet = bdx * cdy - cdx * bdy
    cadet = cdx * ady - adx * cdy
    alift = adx * adx + ady * ady
    blift = bdx * bdx + bdy * bdy
    clift = cdx * cdx + cdy * cdy
    retval = alift * bcdet + blift * cadet + clift * abdet
    if retval > 0.0:
        return Position.INSIDE
    elif retval == 0.0:
        return Position.ON
    return Position.OUTSIDE
