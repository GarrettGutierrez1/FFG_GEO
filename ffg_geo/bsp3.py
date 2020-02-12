# -*- coding: utf-8 -*-
"""bsp3.py

Binary space partitioning (BSP) representation of a mesh in 3D.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import math
from typing import Any, List, Optional, Tuple, Union

from .vector3 import Vector3


class BSP3(object):
    def __init__(self) -> None:
        self.polygons = []  # type: List['BSPPolygon3']

    def __add__(self, other: 'BSP3') -> 'BSP3':
        return self.union(other)

    def __sub__(self, other: 'BSP3') -> 'BSP3':
        return self.subtract(other)

    def __mul__(self, other: 'BSP3') -> 'BSP3':
        return self.intersect(other)

    def clone(self) -> 'BSP3':
        bsp = BSP3()
        bsp.polygons = [polygon.clone() for polygon in self.polygons]
        return bsp

    def union(self, bsp: 'BSP3') -> 'BSP3':
        a = BSPNode3(self.clone().polygons)
        b = BSPNode3(bsp.clone().polygons)
        a.clip_to(b)
        b.clip_to(a)
        b.invert()
        b.clip_to(a)
        b.invert()
        a.build(b.all_polygons())
        return BSP3.from_polygons(a.all_polygons())

    def subtract(self, bsp: 'BSP3') -> 'BSP3':
        a = BSPNode3(self.clone().polygons)
        b = BSPNode3(bsp.clone().polygons)
        a.invert()
        a.clip_to(b)
        b.clip_to(a)
        b.invert()
        b.clip_to(a)
        b.invert()
        a.build(b.all_polygons())
        a.invert()
        return BSP3.from_polygons(a.all_polygons())

    def intersect(self, bsp: 'BSP3') -> 'BSP3':
        a = BSPNode3(self.clone().polygons)
        b = BSPNode3(bsp.clone().polygons)
        a.invert()
        b.clip_to(a)
        b.invert()
        a.clip_to(b)
        b.clip_to(a)
        a.build(b.all_polygons())
        a.invert()
        return BSP3.from_polygons(a.all_polygons())

    def inverse(self) -> 'BSP3':
        bsp = self.clone()
        for polygon in bsp.polygons:
            polygon.flip()
        return bsp

    def save_stl(self, filename: str) -> None:
        import stl
        import numpy
        number_of_triangles = 0
        for polygon in self.polygons:
            number_of_triangles += (len(polygon.vertices) - 2)
        data = numpy.zeros(number_of_triangles, dtype=stl.Mesh.dtype)
        on_triangle = 0
        for polygon in self.polygons:
            for i in range(2, len(polygon.vertices)):
                a, b, c = polygon.vertices[0].pos, polygon.vertices[i - 1].pos, polygon.vertices[i].pos
                n = b.minus(a).cross(c.minus(a)).unit()
                data['vectors'][on_triangle] = numpy.array([[a.x, a.y, a.z], [b.x, b.y, b.z], [c.x, c.y, c.z]])
                data['normals'][on_triangle] = numpy.array([n.x, n.y, n.z])
                on_triangle += 1
        mesh = stl.mesh.Mesh(data)
        mesh.save(filename, mode=stl.Mode.ASCII, update_normals=False)

    @staticmethod
    def from_polygons(polygons: List['BSPPolygon3']) -> 'BSP3':
        bsp = BSP3()
        bsp.polygons = polygons
        return bsp

    @staticmethod
    def load_stl() -> 'BSP3':
        raise NotImplementedError()

    @staticmethod
    def cube(center: Tuple[float, float, float], radius: Union[float, Tuple[float, float, float]]) -> 'BSP3':
        c = Vector3(center[0], center[1], center[2])
        if not isinstance(radius, tuple):
            radius = [float(radius), float(radius), float(radius)]
        r = Vector3(radius[0], radius[1], radius[2])
        polygon_info = [
            [[0, 4, 6, 2], [-1.0, 0.0, 0.0]],
            [[1, 3, 7, 5], [+1.0, 0.0, 0.0]],
            [[0, 1, 5, 4], [0.0, -1.0, 0.0]],
            [[2, 6, 7, 3], [0.0, +1.0, 0.0]],
            [[0, 2, 3, 1], [0.0, 0.0, -1.0]],
            [[4, 5, 7, 6], [0.0, 0.0, +1.0]]
        ]
        polygons = []
        for info in polygon_info:
            vertices = []
            for i in info[0]:
                pos = Vector3(
                    c.x + r.x * (2 * bool(i & 1) - 1),
                    c.y + r.y * (2 * bool(i & 2) - 1),
                    c.z + r.z * (2 * bool(i & 4) - 1)
                )
                # norm = Vector3(info[1][0], info[1][1], info[1][2])
                # vertex = BSPVertex3(pos, norm)
                vertex = BSPVertex3(pos)
                vertices.append(vertex)
            polygon = BSPPolygon3(vertices, None)
            polygons.append(polygon)
        return BSP3.from_polygons(polygons)

    @staticmethod
    def sphere(center: Tuple[float, float, float], radius: float, slices: int, stacks: int) -> 'BSP3':
        c = Vector3(center[0], center[1], center[2])

        def vertex(theta, phi):
            theta *= math.pi * 2.0
            phi *= math.pi
            direction = Vector3(
                math.cos(theta) * math.sin(phi),
                math.cos(phi),
                math.sin(theta) * math.sin(phi)
            )
            # return BSPVertex3(c.plus(direction.times(radius)), direction)
            return BSPVertex3(c.plus(direction.times(radius)))

        polygons = []
        for i in range(slices):
            for j in range(stacks):
                vertices = [vertex(i / slices, j / stacks)]
                if j > 0:
                    vertices.append(vertex((i + 1) / slices, j / stacks))
                if j < (stacks - 1):
                    vertices.append(vertex((i + 1) / slices, (j + 1) / stacks))
                vertices.append(vertex(i / slices, (j + 1) / stacks))
                polygons.append(BSPPolygon3(vertices, None))
        return BSP3.from_polygons(polygons)

    @staticmethod
    def cylinder(start: Tuple[float, float, float], end: Tuple[float, float, float], radius: float,
                 slices: int) -> 'BSP3':
        s = Vector3(start[0], start[1], start[2])
        e = Vector3(end[0], end[1], end[2])
        ray = e.minus(s)
        axis_z = ray.unit()
        is_y = (math.fabs(axis_z.y) > 0.5)
        axis_x = Vector3(float(is_y), float(not is_y), 0.0).cross(axis_z).unit()
        axis_y = axis_x.cross(axis_z).unit()
        # start_vertex = BSPVertex3(s, axis_z.negated())
        start_vertex = BSPVertex3(s)
        # end_vertex = BSPVertex3(e, axis_z.negated())
        end_vertex = BSPVertex3(e)
        polygons = []

        # def point(stack, slice_, normal_blend):
        def point(stack, slice_):
            angle = slice_ * math.pi * 2.0
            out = axis_x.times(math.cos(angle)).plus(axis_y.times(math.sin(angle)))
            pos = s.plus(ray.times(stack)).plus(out.times(radius))
            # normal = out.times(1.0 - math.fabs(normal_blend)).plus(axis_z.times(normal_blend))
            # return BSPVertex3(pos, normal)
            return BSPVertex3(pos)

        for i in range(slices):
            t0 = i / slices
            t1 = (i + 1) / slices
            # polygons.append(BSPPolygon3([start_vertex.clone(), point(0, t0, -1), point(0, t1, -1)], None))
            polygons.append(BSPPolygon3([start_vertex.clone(), point(0, t0), point(0, t1)], None))
            # polygons.append(BSPPolygon3([point(0, t1, 0), point(0, t0, 0), point(1, t0, 0), point(1, t1, 0)], None))
            polygons.append(BSPPolygon3([point(0, t1), point(0, t0), point(1, t0), point(1, t1)], None))
            # polygons.append(BSPPolygon3([end_vertex.clone(), point(1, t1, 0), point(1, t0, 1)], None))
            polygons.append(BSPPolygon3([end_vertex.clone(), point(1, t1), point(1, t0)], None))
        return BSP3.from_polygons(polygons)


class BSPVertex3(object):
    # def __init__(self, pos: 'Vector3', normal: 'Vector3') -> None:
    def __init__(self, pos: 'Vector3') -> None:
        self.pos = Vector3(pos.x, pos.y, pos.z)  # type: Vector3
        # self.normal = Vector3(normal.x, normal.y, normal.z)  # type: Vector3

    def clone(self) -> 'BSPVertex3':
        # return BSPVertex3(self.pos.clone(), self.normal.clone())
        return BSPVertex3(self.pos.clone())

    def flip(self) -> None:
        # self.normal = self.normal.negated()
        pass

    def interpolate(self, other: 'BSPVertex3', t: float) -> 'BSPVertex3':
        # return BSPVertex3(self.pos.lerp(other.pos, t), self.normal.lerp(other.normal, t))
        return BSPVertex3(self.pos.lerp(other.pos, t))


class BSPPlane3(object):
    EPSILON = 1.e-5

    def __init__(self, normal: Vector3, w: float) -> None:
        self.normal = normal
        self.w = w

    def clone(self) -> 'BSPPlane3':
        return BSPPlane3(self.normal.clone(), self.w)

    def flip(self) -> None:
        self.normal = self.normal.negated()
        self.w = -self.w

    def split_polygon(self, polygon: 'BSPPolygon3', coplanar_front: List['BSPPolygon3'],
                      coplanar_back: List['BSPPolygon3'], front: List['BSPPolygon3'],
                      back: List['BSPPolygon3']) -> None:
        coplanar_type = 0
        front_type = 1
        back_type = 2
        spanning_type = 3
        polygon_type = 0
        types = []
        num_vertices = len(polygon.vertices)
        for i in range(num_vertices):
            t = self.normal.dot(polygon.vertices[i].pos) - self.w
            if t < -BSPPlane3.EPSILON:
                vertex_type = back_type
            elif t > BSPPlane3.EPSILON:
                vertex_type = front_type
            else:
                vertex_type = coplanar_type
            polygon_type |= vertex_type
            types.append(vertex_type)
        if polygon_type == coplanar_type:
            t = self.normal.dot(polygon.plane.normal)
            if t > 0:
                coplanar_front.append(polygon)
            else:
                coplanar_back.append(polygon)
        elif polygon_type == front_type:
            front.append(polygon)
        elif polygon_type == back_type:
            back.append(polygon)
        elif polygon_type == spanning_type:
            f = []
            b = []
            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                ti = types[i]
                tj = types[j]
                vi = polygon.vertices[i]
                vj = polygon.vertices[j]
                if ti != back_type:
                    f.append(vi)
                if ti != front_type:
                    if ti != back_type:
                        b.append(vi.clone())
                    else:
                        b.append(vi)
                if (ti | tj) == spanning_type:
                    t = (self.w - self.normal.dot(vi.pos)) / self.normal.dot(vj.pos.minus(vi.pos))
                    v = vi.interpolate(vj, t)
                    f.append(v)
                    b.append(v.clone())
            if len(f) >= 3:
                front.append(BSPPolygon3(f, polygon.shared))
            if len(b) >= 3:
                back.append(BSPPolygon3(b, polygon.shared))

    @staticmethod
    def from_points(a: Vector3, b: Vector3, c: Vector3) -> 'BSPPlane3':
        n = b.minus(a).cross(c.minus(a)).unit()
        return BSPPlane3(n, n.dot(a))


class BSPPolygon3(object):
    def __init__(self, vertices: List[BSPVertex3], shared: Any) -> None:
        self.vertices = vertices
        self.shared = shared
        self.plane = BSPPlane3.from_points(vertices[0].pos, vertices[1].pos, vertices[2].pos)

    def clone(self) -> 'BSPPolygon3':
        vertices = [v.clone() for v in self.vertices]
        return BSPPolygon3(vertices, self.shared)

    def flip(self) -> None:
        self.vertices.reverse()
        for vertex in self.vertices:
            vertex.flip()
        self.plane.flip()


class BSPNode3(object):
    def __init__(self, polygons: Optional[List[BSPPolygon3]] = None) -> None:
        self.plane = None  # type: Optional[BSPPlane3]
        self.front = None  # type: Optional['BSPNode3']
        self.back = None  # type: Optional['BSPNode3']
        self.polygons = []  # type: List[BSPPolygon3]
        if polygons is not None and len(polygons) > 0:
            self.build(polygons)

    def clone(self) -> 'BSPNode3':
        node = BSPNode3()
        if self.plane is not None:
            node.plane = self.plane.clone()
        if self.front is not None:
            node.front = self.front.clone()
        if self.back is not None:
            node.back = self.back.clone()
        node.polygons = [p.clone() for p in self.polygons]
        return node

    def invert(self) -> None:
        for polygon in self.polygons:
            polygon.flip()
        if self.plane is not None:
            self.plane.flip()
        if self.front is not None:
            self.front.invert()
        if self.back is not None:
            self.back.invert()
        temp = self.front
        self.front = self.back
        self.back = temp

    def clip_polygons(self, polygons: List[BSPPolygon3]) -> List[BSPPolygon3]:
        if self.plane is None:
            return polygons[:]
        front = []
        back = []
        for polygon in polygons:
            self.plane.split_polygon(polygon, front, back, front, back)
        if self.front is not None:
            front = self.front.clip_polygons(front)
        if self.back is not None:
            back = self.back.clip_polygons(back)
        else:
            back = []
        front.extend(back)
        return front

    def clip_to(self, bsp: 'BSPNode3') -> None:
        self.polygons = bsp.clip_polygons(self.polygons)
        if self.front is not None:
            self.front.clip_to(bsp)
        if self.back is not None:
            self.back.clip_to(bsp)

    def all_polygons(self) -> List[BSPPolygon3]:
        polygons = self.polygons[:]
        if self.front is not None:
            polygons.extend(self.front.all_polygons())
        if self.back is not None:
            polygons.extend(self.back.all_polygons())
        return polygons

    def build(self, polygons: List[BSPPolygon3]) -> None:
        if len(polygons) < 1:
            return
        if self.plane is None:
            self.plane = polygons[0].plane.clone()
        self.polygons.append(polygons[0])
        front = []
        back = []
        for polygon in polygons[1:]:
            self.plane.split_polygon(polygon, self.polygons, self.polygons, front, back)
        if len(front) > 0:
            if self.front is None:
                self.front = BSPNode3()
            self.front.build(front)
        if len(back) > 0:
            if self.back is None:
                self.back = BSPNode3()
            self.back.build(back)
