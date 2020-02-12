# -*- coding: utf-8 -*-
"""ifs3.py

Indexed face set (IFS) representation of a mesh in 3D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

from typing import Iterable, List, Optional

from .vector3 import Vector3


class IFSVertex3(object):
    """Vertex in an indexed face set.

    Attributes:
        position: Vector position of the vertex.
        data: Optional data index, used for associating vertices with data external to the IFS."""
    def __init__(self, position: Vector3, data: Optional[int] = None) -> None:
        """Initializes the IFSVertex3.

        Args:
            position: Vector position of the vertex.
            data: Optional data index, used for associating vertices with data external to the IFS."""
        self.position = position
        self.data = data


class IFSTriangle3(object):
    """Vertex in an indexed face set.

    Attributes:
        vertices: Indices of the vertices. Counter-clockwise order.
        data: Optional data index, used for associating triangles with data external to the IFS."""
    def __init__(self, vertices: Iterable[int], data: Optional[int] = None) -> None:
        """Initializes the IFSTriangle3.

        Args:
            vertices: Indices of the vertices. Counter-clockwise order.
            data: Optional data index, used for associating triangles with data external to the IFS."""
        self.vertices = [value for value in vertices[:3]]
        self.data = data


class IFS3(object):
    """IFS mesh representation.

    Attributes:
        vertices: List of IFSVertex3 vertices.
        triangles: List of IFSTriangle3 triangles."""
    def __init__(self, vertices: Optional[List[IFSVertex3]] = None, triangles: Optional[List[IFSTriangle3]] = None) -> \
            None:
        """Initializes the IFS3.

        Args:
            vertices: List of IFSVertex3 vertices.
            triangles: List of IFSTriangle3 triangles."""
        if vertices is None:
            vertices = []
        if triangles is None:
            triangles = []
        self.vertices = vertices  # type: List[IFSVertex3]
        self.triangles = triangles  # type: List[IFSTriangle3]
