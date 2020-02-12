# -*- coding: utf-8 -*-
"""heds3.py

Half-edge data structure (HEDS) representation of a mesh in 3D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

from typing import List, Optional

from .vector3 import Vector3


class HEDSHalfEdge3(object):
    """Half-edge in an HEDS.

    Attributes:
        source: The index of the source vertex for the half-edge.
        face: The index of the face adjacent to the half-edge.
        successor: The index of the successor half-edge to the half-edge."""
    def __init__(self, source: int, face: int, successor: int) -> None:
        """Initializes the HEDSHalfEdge3.

        Args:
            source: The index of the source vertex for the half-edge.
            face: The index of the face adjacent to the half-edge.
            successor: The index of the successor half-edge to the half-edge."""
        self.source = source
        self.face = face
        self.successor = successor


class HEDSVertex3(object):
    """Vertex in a HEDS.

    Attributes:
        position: The position vector of the vertex.
        in_halfedge: The index of an arbitrary half-edge going into the vertex.
        data: Optional data index, used for associating vertices with data external to the HEDS."""
    def __init__(self, position: Vector3, in_halfedge: int, data: Optional[int] = None) -> None:
        """Initializes the HEDSVertex3.

        Args:
            position: The position vector of the vertex.
            in_halfedge: The index of an arbitrary half-edge going into the vertex.
            data: Optional data index, used for associating vertices with data external to the HEDS."""
        self.position = position
        self.in_halfedge = in_halfedge
        self.data = data


class HEDSFace3(object):
    """Face in a HEDS.

    Attributes:
        halfedge: The index of an arbitrary half-edge on the boundary of the face.
        hole: Optional index of the first hole in the list of holes in this face. None if there are no holes.
        data: Optional data index, used for associating faces with data external to the HEDS."""
    def __init__(self, halfedge: int, hole: Optional[int] = None, data: Optional[int] = None) -> None:
        """Initializes the HEDSFace3.

        Args:
            halfedge: The index of an arbitrary half-edge on the boundary of the face.
            hole: Optional index of the first hole in the list of holes in this face. None if there are no holes.
            data: Optional data index, used for associating faces with data external to the HEDS."""
        self.halfedge = halfedge
        self.hole = hole
        self.data = data


class HEDSHole3(object):
    """Hole in a face in a HEDS.

    Attributes:
        halfedge: The index of an arbitrary half-edge ont he boundary of the face.
        successor: Optional index of the successor hole to this hole. None if there is no successor to this hole."""
    def __init__(self, halfedge: int, successor: Optional[int] = None) -> None:
        """Initializes the HEDSHole3.

        Args:
            halfedge: The index of an arbitrary half-edge ont he boundary of the face.
            successor: Optional index of the successor hole to this hole. None if there is no successor to this hole."""
        self.halfedge = halfedge
        self.successor = successor


class HEDS3(object):
    """Half-edge data structure mesh representation.

    Attributes:
        halfedges: List of HEDSHalfEdge3 half-edges.
        vertices: List of HEDSVertex3 vertices.
        faces: List of HEDSFace3 faces.
        holes: List of HEDSHole3 holes."""
    def __init__(self, halfedges: Optional[List[HEDSHalfEdge3]] = None, vertices: Optional[List[HEDSVertex3]] = None,
                 faces: Optional[List[HEDSFace3]] = None, holes: Optional[List[HEDSHole3]] = None) -> None:
        """Initializes the HEDS3.

        Args:
            halfedges: List of HEDSHalfEdge3 half-edges.
            vertices: List of HEDSVertex3 vertices.
            faces: List of HEDSFace3 faces.
            holes: List of HEDSHole3 holes."""
        if halfedges is None:
            halfedges = []
        if vertices is None:
            vertices = []
        if faces is None:
            faces = []
        if holes is None:
            holes = []
        self.halfedges = halfedges  # type: List[HEDSHalfEdge3]
        self.vertices = vertices  # type: List[HEDSVertex3]
        self.faces = faces  # type: List[HEDSFace3]
        self.holes = holes  # type: List[HEDSHole3]
