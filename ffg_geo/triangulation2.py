# -*- coding: utf-8 -*-
"""triangulation2.py

A module implementing Triangulation2, which serves as the vehicle for triangulating vertices.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import collections
import copy
import enum
import math
from typing import Deque, List, Optional, Set, Tuple

from ffg_geo.predicates import in_circle, Orientation, Position, side
from ffg_geo.triangle2 import Triangle2
from ffg_geo.vector2 import Vector2
from ffg_geo.window import Window


class MergeMethod(enum.Enum):
    ARBITRARY = 0
    FLIP = 1
    DELAUNAY = 2


class CutMethod(enum.Enum):
    VERTICAL = 0
    HORIZONTAL = 1
    ALTERNATING = 2


class Triangulation2(object):
    """
    A class representing a (potentially constrained) (potentially Delaunay) triangulation.

    Algorithm:
        Delaunay triangulation is done here using a recursive binary divide-and-conquer algorithm with vertical,
        horizontal, or alternating. Triangles are represented using an indexed triangular data structure (rather than a
        quad-edge data structure) with ghost triangles at the hull(s).

    Indexed Triangle Data Structure:
        In addition to maintaining indices to their 3 vertices, all triangles maintain indices to their 3 neighbors.
        Both are maintained in counter-clockwise order. For every non-ghost triangle, its i-th neighbor is the triangle
        opposite the edge between its vertices i and (i + 1) % 3.

    Ghost Triangles:
        Ghost triangles exist at the hull(s) of a triangulation. For every ghost triangle, its vertices 0 and 1 are both
        indices while its vertex 2 is None, indicating that it is a ghost triangle. In addition, only one of its
        neighbors, neighbor 0 (opposite the edge (0, 1)) is directly adjacent to it. The other neighbors 1 and 2 are the
        ghost triangles to the right (clockwise) and left (counter-clockwise) of the ghost triangle on the hull. In this
        way any hull can be traversed so long as the index of one ghost triangle on the hull is known. Non-ghost
        triangles are called existent triangles.

    Special Case: Co-linear Vertices:
        If and only if all vertices in the triangulation are co-linear and the number of vertices is >1, the
        triangulation will consist only of ghost triangles such that their neighbor 0, also a ghost triangle, share an
        edge and that edge is an actual edge in the triangulation as well as a segment of the line joining all the
        co-linear vertices. In that way triangulations of co-linear vertices consist only of connected co-linear line
        segment edges.

    Special Case: 0 or 1 Unique Vertices:
        Triangulations of 0 or 1 unique vertices will contain no triangles (ghost or otherwise) or edges.

    Duplicate Vertices:
        Duplicate vertices will be removed from the vertices list.

    Vertex Ordering:
        The ordering of the vertices will not be maintained after triangulation.

    Vertical Cuts:
        Vertical cuts are used, meaning that for every recursive triangulation you can imagine that a vertical line is
        drawn such that half the vertices being triangulated are on the left of the line and the other half are on the
        right of the line (some vertices from either side may be on the line). After both sets of vertices are
        independently recursively triangulated, both halves are merged.

    Merging:
        The merge is done by first arbitrarily merging both triangulations such that the triangles created in the merge
        are not delaunay. The edges are then iterated over and flipped as necessary until the triangulation is delaunay.

    Properties Maintained:
        For all methods of this class, be they public or private, except for triangulate, the following properties are
        assumed upon entrance and maintained upon exit.
            Vertex Properties:
                - All vertices are unique.
                - The vertices are in x increasing, y increasing order.
            Triangle Properties:
                - All triangles are unique.
                - The i-th neighbor of a triangle is its neighbor opposite the edge connecting its i-th neighbor and its
                  (i + 1) % 3rd neighbor, assuming both indices are not None.
            Existent Triangle Properties:
                - For every existent triangle, its vertices are in counter-clockwise order.
                - For every existent triangle, it is locally Delaunay assuming either this is not a CDT or the
                  constraints of the CDT have not yet been enforced.
            Ghost Triangle Properties:
                - For every ghost triangle, it exists on the hull, external or internal (in the case of holes in a CDT),
                  of the complete triangulation of some vertex partition.
                - For every ghost triangle, vertices 0 and 1 are indices while vertex 2 is None.
                - For every ghost triangle, neighbor 0 is an existent triangle while neighbors 1 and 2 are ghost
                  triangles.
                - For every ghost triangle, neighbor 1 is the ghost triangle adjacent to it clockwise on the
                  hull if it is external or counter-clockwise to it on the hull if it is internal. This is called the
                  ghost triangle's clockwise or right neighbor.
                - For every ghost triangle, neighbor 2 is the ghost triangle adjacent to it counter-clockwise on the
                  hull if it is internal or clockwise to it on the hull if it is external. This is called the ghost
                  triangle's left neighbor.
            Edge Properties:
                - Every edge has two triangles on either side of it. If this is a hull edge on a triangulation of non-
                  co-linear vertices, one triangle is a ghost and the other is existent. If this is a hull edge on the
                  triangulation of co-linear vertices, both triangles are ghost triangles. If this an internal edge,
                  both triangles are existent.

    Attributes:
        vertices: The vertices to triangulate.
        segments: The segments of the CDT.
        triangles: The triangles created as a result of the triangulation.
        window: The window to draw to. Optional.
        display_mode: If images drawn should appear on the screen or be written to a video.
        order: The order to draw elements when drawing.
    """
    def __init__(self, vertices: List[Vector2], segments: Optional[List[Tuple[int, int]]] = None,
                 window: Optional[Window] = None, display_mode: bool = True, order: str = 'geshv') -> None:
        """
        Initializes the Triangulation2.

        Args:
            vertices: The vertices to triangulate.
            segments: The segments of the CDT.
            window: An optional Window. If it is not None, upon drawing the Triangulation2 will either display or save
            an image depicting its current state.
            display_mode: If drawn images should be displayed (if False, they will be saved). Only relevant if window is
            not None.
            order: The order to draw elements when drawing. See the description of the order arg for the draw method.
        """
        self.vertices = vertices
        self.indices = []
        if segments is None:
            self.__segments = []
        else:
            self.__segments = segments
        self.triangles = []  # type: List[Triangle2]
        self.window = window
        self.display_mode = display_mode
        self.order = order

    def triangulate(self, merge_method: MergeMethod, cut_method: CutMethod) -> None:
        """Triangulates the vertices using a recursive divide-and-conquer method using the specified merge and and cut
        methods.

        Args:
            merge_method: The method to merge with.
            cut_method: The method to cut with.
        """
        self.triangles = []

        # TODO: Implement.
        if merge_method is MergeMethod.FLIP or merge_method is MergeMethod.DELAUNAY:
            raise Exception('NOT IMPLEMENTED.')

        # TODO: Implement.
        if cut_method is CutMethod.HORIZONTAL or cut_method is CutMethod.ALTERNATING:
            raise Exception('NOT IMPLEMENTED.')

        # Sort in accordance with cut method.
        self.__sort(cut_method)

        # Cannot triangulate 1 point.
        if len(self.vertices) < 2:
            return

        # Triangulate recursively.
        self.__divide_and_conquer(0, len(self.vertices))

    def __sort(self, cut_method: CutMethod) -> None:
        """Sorts the vertices according to the kind of cuts that will be used in the divide-and-conquer portion of the
        triangulation.

        Args:
            cut_method: The method to cut with.
        """
        if len(self.vertices) < 2:
            return

        # Sort the vertices so that duplicates can be discarded.
        if cut_method is CutMethod.HORIZONTAL:
            enumerated_vertices = sorted(enumerate(self.vertices), key=lambda vp: (vp[1][1], vp[1][0]))
        else:
            enumerated_vertices = sorted(enumerate(self.vertices), key=lambda vp: (vp[1][0], vp[1][1]))

        # Eliminate duplicates.
        self.vertices = []
        self.indices = [None] * len(enumerated_vertices)  # type: List[Optional[int]]
        self.vertices.append(enumerated_vertices[0][1])
        self.indices[enumerated_vertices[0][0]] = 0
        for index, vertex in enumerated_vertices[1:]:
            if self.vertices[len(self.vertices) - 1] == vertex:
                self.indices[index] = len(self.vertices) - 1
                continue
            self.indices[index] = len(self.vertices)
            self.vertices.append(vertex)

        # TODO: Implement.
        # Sort for alternating cuts.
        if cut_method is CutMethod.ALTERNATING:
            raise Exception('NOT IMPLEMENTED.')

        # Adjust the segments.
        old_segments = self.__segments
        self.__segments = []
        for old_segment in old_segments:
            new_segment = (self.indices[old_segment[0]], self.indices[old_segment[1]])
            new_segment = (min(new_segment), max(new_segment))
            self.__segments.append(new_segment)

    # def debug_print(self) -> None:
    #     print('-------------------- DEBUG --------------------')
    #     for index, vertex in enumerate(self.vertices):
    #         print('{}: {}'.format(index, vertex.to_str()))
    #     for index, triangle in enumerate(self.triangles):
    #         print('{}: {}'.format(index, triangle))
    #     print('-------------------- DEBUG --------------------')

    def draw(self, n: int = 1, order: str = 'geshv', radius: int = 3,
             vertex_color: Tuple[float, float, float] = (255.0, 255.0, 255.0),
             edge_color: Tuple[float, float, float] = (255.0, 255.0, 255.0),
             ghost_color: Tuple[float, float, float] = (0.0, 0.0, 255.0),
             segment_color: Tuple[float, float, float] = (255.0, 0.0, 0.0), real_thickness: int = 1,
             ghost_thickness: int = 1, ghost_factor: float = 0.05) -> None:
        """Draws the triangulation. Assumes the window's coordinate system has already been set to fit the vertices.
        Does nothing if no window was provided to the constructor.

        Args:
            n: How many times to draw.
            order: The order to draw elements. Composed of the following characters:
                'g': Ghost edges.
                'e': Regular edges.
                's': Segment edges.
                'h': Ghost vertices.
                'v': Regular vertices.
            radius: The radius of vertices (in pixels).
            vertex_color: The color of existent vertices (BGR).
            edge_color: The color of regular edges (BGR).
            ghost_color: The color of ghost edges and vertices (BGR).
            segment_color: The color of segment edges (BGR).
            real_thickness: The thickness of existent edges (regular and segment, in pixels).
            ghost_thickness: The thickness of ghost edges (in pixels).
            ghost_factor: The distance of ghost vertices from their corresponding hull edges as a percentage of the hull
                edge length.
        """
        if self.window is None:
            return
        self.window.flush()
        vertices_copy = copy.deepcopy(self.vertices)
        triangles_copy = copy.deepcopy(self.triangles)
        segment_edges = set()
        ghost_edges = set()
        inner_edges = set()
        drawn_edges = set()
        for t in triangles_copy:
            if t.v[2] is None:
                v_0 = vertices_copy[t.v[0]]
                v_1 = vertices_copy[t.v[1]]
                v_2 = v_0.lerp(v_1, 0.5)
                v_t = v_1 - v_0
                v_t = v_t.rotated(math.pi * 0.5)
                v_t = v_t * ghost_factor
                v_2 = v_2 + v_t
                vertices_copy.append(v_2)
                t.v[2] = len(vertices_copy) - 1
        for edge in self.__segments:
            edge = (min(edge), max(edge))
            segment_edges.add(edge)
        for t in triangles_copy:
            for edge in [(t.v[i], t.v[(i + 1) % 3]) for i in range(3)]:
                edge = (min(edge), max(edge))
                if edge in segment_edges:
                    continue
                if edge[1] >= len(self.vertices):
                    ghost_edges.add(edge)
                else:
                    inner_edges.add(edge)
        for char in order:
            if char == 'g':
                for edge in ghost_edges:
                    if edge not in drawn_edges:
                        self.window.draw_line(vertices_copy[edge[0]], vertices_copy[edge[1]], ghost_color,
                                              ghost_thickness)
                        drawn_edges.add(edge)
            elif char == 'e':
                for edge in inner_edges:
                    if edge not in drawn_edges:
                        self.window.draw_line(vertices_copy[edge[0]], vertices_copy[edge[1]], edge_color,
                                              real_thickness)
                        drawn_edges.add(edge)
            elif char == 's':
                for edge in segment_edges:
                    if edge not in drawn_edges:
                        self.window.draw_line(vertices_copy[edge[0]], vertices_copy[edge[1]], segment_color,
                                              real_thickness)
            elif char == 'h':
                for v in vertices_copy[len(self.vertices):]:
                    self.window.draw_circle(v, radius, ghost_color, -1)
            elif char == 'v':
                for v in self.vertices:
                    self.window.draw_circle(v, radius, vertex_color, -1)
        if self.display_mode:
            self.window.display()
        else:
            for _ in range(n):
                self.window.save_image()

    def __side(self, a: int, b: int, c: int) -> Orientation:
        """Vector sideness predicate.

        Args:
            a: The index of the source vector.
            b: The index of the destination vector.
            c: The index of the vector to determine sideness of w.r.t. (a,b).

        Returns:
            The orientation (left, right, or co-linear).
        """
        return side(self.vertices[a], self.vertices[b], self.vertices[c])

    def __in_circle(self, t: int, d: Vector2) -> Position:
        """Vector in-circle predicate.

        Args:
            t: The triangle with counter-clockwise vertices (a,b,c).
            d: Vector d to test the position of w.r.t. (a,b,c).

        Returns:
            The position (in-circle, out-circle, or on-circle).
        """
        triangle = self.triangles[t]
        a = self.vertices[triangle.v[0]]
        b = self.vertices[triangle.v[1]]
        c = self.vertices[triangle.v[2]]
        return in_circle(a, b, c, d)

    def __trivial_triangulation(self, begin: int, end: int) -> Tuple[int, int, int, int]:
        """Trivial triangulation of 2 or 3 vertices.

        Note:
            The assumption is made upon entering this method that 2 <= |[begin, end)| <= 3. Behavior is undefined
            otherwise.

        Args:
            begin: The beginning of the range of vertices to triangulate (inclusive).
            end: The end of the range of vertices to triangulate (exclusive).

        Returns:
            Triangles 2, 3, 6, and 7 of the triangulation.
        """
        # TODO: Make this also return triangles 0, 1, 4, and 5 of the triangulation.
        # NOTE: We need to do this in order to support horizontal or alternating cuts.
        # NOTE: This should be very straight forward.
        num = end - begin
        num_t = len(self.triangles)
        if num < 3:
            # There are 2 vertices. Connect them as an edge.
            # t_0 is the ghost triangle with the ghost vertex to the left of the edge connecting the vertices in order.
            # t_1 is the ghost triangle on the opposite side of the edge.
            t_0 = Triangle2((begin, begin + 1, None), (num_t + 1, num_t + 1, num_t + 1))
            t_1 = Triangle2((begin + 1, begin, None), (num_t, num_t, num_t))
            self.triangles.append(t_0)
            self.triangles.append(t_1)
            return num_t, num_t + 1, num_t + 1, num_t
        else:
            # There are 3 vertices. Connect them as a triangle if they are not co-linear.
            orientation = self.__side(begin, begin + 1, begin + 2)
            if orientation is Orientation.LEFT:
                # The 3rd vertex is to the left of the edge connecting the first 2 vertices in order.
                print('Trivial: Oriented left.')
                end_pt = begin + 1
                left_pt = begin + 2
                t_0 = Triangle2((begin, end_pt, left_pt), (num_t + 1, num_t + 2, num_t + 3))
                t_1 = Triangle2((end_pt, begin, None), (num_t, num_t + 3, num_t + 2))
                t_2 = Triangle2((left_pt, end_pt, None), (num_t, num_t + 1, num_t + 3))
                t_3 = Triangle2((begin, left_pt, None), (num_t, num_t + 2, num_t + 1))
                self.triangles.append(t_0)
                self.triangles.append(t_1)
                self.triangles.append(t_2)
                self.triangles.append(t_3)
                return num_t + 3, num_t + 1, num_t + 2, num_t + 3
            elif orientation is Orientation.RIGHT:
                # The 3rd vertex is to the right of the edge connecting the first 2 vertices in order.
                print('Trivial: Oriented right.')
                end_pt = begin + 2
                left_pt = begin + 1
                t_0 = Triangle2((begin, end_pt, left_pt), (num_t + 1, num_t + 2, num_t + 3))
                t_1 = Triangle2((end_pt, begin, None), (num_t, num_t + 3, num_t + 2))
                t_2 = Triangle2((left_pt, end_pt, None), (num_t, num_t + 1, num_t + 3))
                t_3 = Triangle2((begin, left_pt, None), (num_t, num_t + 2, num_t + 1))
                self.triangles.append(t_0)
                self.triangles.append(t_1)
                self.triangles.append(t_2)
                self.triangles.append(t_3)
                return num_t + 3, num_t + 1, num_t + 1, num_t + 2
            # The 3 vertices are co-linear.
            print('Trivial: Oriented co-linear.')
            t_0 = Triangle2((begin, begin + 1, None), (num_t + 1, num_t + 2, num_t + 1))
            t_1 = Triangle2((begin + 1, begin, None), (num_t, num_t, num_t + 3))
            t_2 = Triangle2((begin + 1, begin + 2, None), (num_t + 3, num_t + 3, num_t))
            t_3 = Triangle2((begin + 2, begin + 1, None), (num_t + 2, num_t + 1, num_t + 2))
            self.triangles.append(t_0)
            self.triangles.append(t_1)
            self.triangles.append(t_2)
            self.triangles.append(t_3)
            return num_t, num_t + 1, num_t + 3, num_t + 2

    def __merge_arbitrary(self, tri_l6: int, tri_l7: int, tri_r2: int, tri_r3: int) -> None:
        """Merges 2 triangulations.

        Args:
            tri_l6: Triangle 6 of the left triangulation.
            tri_l7: Triangle 7 of the left triangulation.
            tri_r2: Triangle 2 of the right triangulation.
            tri_r3: Triangle 3 of the right triangulation.
        """
        # TODO: Make this work with horizontal and alternating cuts.
        # NOTE: It should implicitly work with alternating cuts as it is written now so long as the following are true:
        # NOTE: - tri_l6 is actually tri_d0.
        # NOTE: - tri_l7 is actually tri_d1.
        # NOTE: - tri_r2 is actually tri_u4.
        # NOTE: - tri_r3 is actually tri_u5.
        # TODO: Create a version of this method that flips the edges it creates.
        # NOTE: To do this, do the following:
        # NOTE: - Look at the __enforce_delaunay method. The portion that iterates through the edge queue should be the
        # NOTE:   exact same.
        # NOTE: - Every time you resurrect a triangle (one in each loop and once in the very beginning) add the edge
        # NOTE:   created to the edge queue. The very first resurrection is unique in that it creates two edges. In
        # NOTE:   addition, add every hull edge (the base of the resurrected triangle) to tbe edge queue. Why? We can
        # NOTE:   envision a scenario I think where the edge created might be locally delaunay but the previous hull
        # NOTE:   edge might not be.
        num_t = len(self.triangles)
        # lr_v: the index of the left triangulation's right most vertex.
        # lru_v: the index of the vertex counter-clockwise lr_v on the hull.
        # lrd_v: the index of the vertex clockwise lr_v on the hull.
        # rl_v: the index of the right triangulation's left most vertex.
        # rlu_v: the index of the vertex clockwise rl_v on the hull.
        # rld_v: the index of the vertex counter-clockwise rld_v on the hull.
        lr_v = self.triangles[tri_l6].v[0]
        lru_v = self.triangles[tri_l7].v[0]
        lrd_v = self.triangles[tri_l6].v[1]
        rl_v = self.triangles[tri_r2].v[0]
        rlu_v = self.triangles[tri_r2].v[1]
        rld_v = self.triangles[tri_r3].v[0]
        if self.__side(lru_v, lr_v, rl_v) is Orientation.LEFT:
            # We can begin by resurrecting tri_l7
            initial_tri = tri_l7
            initial_v = rl_v
            initial_based_left = True
            initial_opposite_tri = tri_r2
            later_opposite_tri = tri_r3
        elif self.__side(lrd_v, lr_v, rl_v) is Orientation.RIGHT:
            # We can begin by resurrecting tri_l6
            initial_tri = tri_l6
            initial_v = rl_v
            initial_based_left = True
            initial_opposite_tri = tri_r2
            later_opposite_tri = tri_r3
        elif self.__side(lr_v, rl_v, rlu_v) is Orientation.LEFT:
            # We can begin by resurrecting tri_r2
            initial_tri = tri_r2
            initial_v = lr_v
            initial_based_left = False
            initial_opposite_tri = tri_l7
            later_opposite_tri = tri_l6
        elif self.__side(lr_v, rl_v, rld_v) is Orientation.RIGHT:
            # We can begin by resurrecting tri_r3
            initial_tri = tri_r3
            initial_v = lr_v
            initial_based_left = False
            initial_opposite_tri = tri_l7
            later_opposite_tri = tri_l6
        else:
            # We are dealing with co-linear points.
            t_0 = Triangle2((lr_v, rl_v, None), (num_t + 1, tri_r2, tri_l7))
            t_1 = Triangle2((rl_v, lr_v, None), (num_t + 0, tri_l6, tri_r3))
            self.triangles[tri_l7].n[1] = num_t + 0
            self.triangles[tri_r2].n[2] = num_t + 0
            self.triangles[tri_l6].n[2] = num_t + 1
            self.triangles[tri_r3].n[1] = num_t + 1
            self.triangles.append(t_0)
            self.triangles.append(t_1)
            return
        # Resurrect initial_tri.
        self.triangles[initial_tri].v[2] = initial_v
        # Stitch above the initial triangle.
        based_left = initial_based_left
        current_tri = initial_tri
        opposite_tri = initial_opposite_tri
        while True:
            # FIXME: Get rid of draws when debugging not necessary.
            self.draw(order=self.order)
            # First we determine the following indices:
            # l_v: The upper left vertex on the most recently resurrect ghost triangle.
            # r_v: The upper right vertex on the most recently resurrect ghost triangle.
            # lu_v: The vertex counter-clockwise of l_v on the left triangulation's hull.
            # ru_v: The vertex clockwise of r_v on the right triangulation's hull.
            # How we get these values is different depending on if the resurrected triangle is from the left or right
            # triangulation.
            if based_left:
                l_v = self.triangles[current_tri].v[0]
                r_v = self.triangles[current_tri].v[2]
                lg_tri = self.triangles[current_tri].n[2]
                rg_tri = opposite_tri
                lu_v = self.triangles[lg_tri].v[0]
                ru_v = self.triangles[opposite_tri].v[1]
                c_tri_neighbor = 2
            else:
                l_v = self.triangles[current_tri].v[2]
                r_v = self.triangles[current_tri].v[1]
                lg_tri = opposite_tri
                rg_tri = self.triangles[current_tri].n[1]
                lu_v = self.triangles[opposite_tri].v[0]
                ru_v = self.triangles[rg_tri].v[1]
                c_tri_neighbor = 1
            # We now have the specified vertices and can determine which triangle to resurrect.
            if self.__side(lu_v, l_v, r_v) is Orientation.LEFT:
                # We can resurrect the left triangle.
                # Resurrect it.
                self.triangles[lg_tri].v[2] = r_v
                # Make the two recently resurrected triangles neighbors.
                self.triangles[lg_tri].n[1] = current_tri
                self.triangles[current_tri].n[c_tri_neighbor] = lg_tri
                # Update the information we need for the next iteration.
                if not based_left:
                    opposite_tri = rg_tri
                    # opposite_tri = self.triangles[opposite_tri].n[2]
                based_left = True
                current_tri = lg_tri
            elif self.__side(ru_v, r_v, l_v) is Orientation.RIGHT:
                # We can resurrect the right triangle.
                # Resurrect it.
                self.triangles[rg_tri].v[2] = l_v
                # Make the two recently resurrected triangles neighbors.
                self.triangles[rg_tri].n[2] = current_tri
                self.triangles[current_tri].n[c_tri_neighbor] = rg_tri
                # Update the information we need for the next iteration.
                if based_left:
                    opposite_tri = lg_tri
                    # opposite_tri = self.triangles[opposite_tri].n[1]
                based_left = False
                current_tri = rg_tri
            else:
                # We cannot stitch upwards anymore.
                # Create a new ghost triangle and break.
                num_tri = len(self.triangles)
                if based_left:
                    rg_tri = opposite_tri
                    lg_tri = self.triangles[current_tri].n[2]
                    self.triangles[current_tri].n[2] = num_tri
                else:
                    rg_tri = self.triangles[current_tri].n[1]
                    lg_tri = opposite_tri
                    self.triangles[current_tri].n[1] = num_tri
                self.triangles[rg_tri].n[2] = num_tri
                self.triangles[lg_tri].n[1] = num_tri
                new_ghost = Triangle2((l_v, r_v, None), (current_tri, rg_tri, lg_tri))
                self.triangles.append(new_ghost)
                break
        # Stitch below the initial triangle.
        based_left = initial_based_left
        current_tri = initial_tri
        opposite_tri = later_opposite_tri
        while True:
            # FIXME: Get rid of draws when debugging not necessary.
            self.draw(order=self.order)
            if based_left:
                l_v = self.triangles[current_tri].v[1]
                r_v = self.triangles[current_tri].v[2]
                lg_tri = self.triangles[current_tri].n[1]
                rg_tri = opposite_tri
                ld_v = self.triangles[lg_tri].v[1]
                rd_v = self.triangles[opposite_tri].v[0]
                c_tri_neighbor = 1
            else:
                l_v = self.triangles[current_tri].v[2]
                r_v = self.triangles[current_tri].v[0]
                lg_tri = opposite_tri
                rg_tri = self.triangles[current_tri].n[2]
                ld_v = self.triangles[opposite_tri].v[1]
                rd_v = self.triangles[rg_tri].v[0]
                c_tri_neighbor = 2
            if self.__side(ld_v, l_v, r_v) is Orientation.RIGHT:
                # We can resurrect the left triangle.
                # Resurrect it.
                self.triangles[lg_tri].v[2] = r_v
                # Make the two recently resurrected triangles neighbors.
                self.triangles[lg_tri].n[2] = current_tri
                self.triangles[current_tri].n[c_tri_neighbor] = lg_tri
                # Update the information we need for the next iteration.
                if not based_left:
                    opposite_tri = rg_tri
                    # opposite_tri = self.triangles[opposite_tri].n[1]
                based_left = True
                current_tri = lg_tri
            elif self.__side(rd_v, r_v, l_v) is Orientation.LEFT:
                # We can resurrect the right triangle.
                # Resurrect it.
                self.triangles[rg_tri].v[2] = l_v
                # Make the two recently resurrected triangles neighbors.
                self.triangles[rg_tri].n[1] = current_tri
                self.triangles[current_tri].n[c_tri_neighbor] = rg_tri
                # Update the information we need for the next iteration.
                if based_left:
                    opposite_tri = lg_tri
                    # opposite_tri = self.triangles[opposite_tri].n[2]
                based_left = False
                current_tri = rg_tri
            else:
                # We cannot stitch downwards anymore.
                # Create a new ghost triangle and break.
                num_tri = len(self.triangles)
                if based_left:
                    rg_tri = self.triangles[current_tri].n[1]
                    lg_tri = opposite_tri
                    self.triangles[current_tri].n[1] = num_tri
                else:
                    rg_tri = opposite_tri
                    lg_tri = self.triangles[current_tri].n[2]
                    self.triangles[current_tri].n[2] = num_tri
                self.triangles[rg_tri].n[2] = num_tri
                self.triangles[lg_tri].n[1] = num_tri
                new_ghost = Triangle2((r_v, l_v, None), (current_tri, rg_tri, lg_tri))
                self.triangles.append(new_ghost)
                break

    def __find_ghosts(self, tri_l2: int, tri_l3: int, tri_r6: int, tri_r7: int) -> Tuple[int, int, int, int]:
        """Finds ghost triangles 2, 3, 6, and 7 immediately after the merge step from triangles 2 and 3 of the left
        triangulation and triangles 6 and 7 of the right triangulation. After merging, any of the aforementioned ghost
        triangles from the triangulations prior to the merge may be resurrected. We find the actual post-merge triangles
        2, 3, 6, and 7 by moving towards the hull from the previous 2, 3, 6, and 7 until we find the ghost triangles.

        Args:
            tri_l2: Triangle 2 of the left triangulation prior to the merge.
            tri_l3: Triangle 3 of the left triangulation prior to the merge.
            tri_r6: Triangle 6 of the right triangulation prior to the merge.
            tri_r7: Triangle 7 of the right triangulation prior to the merge.

        Returns:
            tri_2: Triangle 2 of the merged triangulation.
            tri_3: Triangle 3 of the merged triangulation.
            tri_6: Triangle 6 of the merged triangulation.
            tri_7: Triangle 7 of the merged triangulation.
        """
        # TODO: Figure out how to fix tri_d0, tri_d1, tri_u4, and tri_u5.
        # NOTE: This method might suffice as it is now if I pass them in. It might not. Look into it.
        # Find triangle 2 from tri_l2.
        first_done = False
        while self.triangles[tri_l2].v[2] is not None:
            if first_done:
                tri_l2 = self.triangles[tri_l2].n[1]
            else:
                tri_l2 = self.triangles[tri_l2].n[2]
                first_done = True
        # Find triangle 3 from tri_l3.
        first_done = False
        while self.triangles[tri_l3].v[2] is not None:
            if first_done:
                tri_l3 = self.triangles[tri_l3].n[2]
            else:
                tri_l3 = self.triangles[tri_l3].n[1]
                first_done = True
        # Find triangle 6 from tri_r6.
        first_done = False
        while self.triangles[tri_r6].v[2] is not None:
            if first_done:
                tri_r6 = self.triangles[tri_r6].n[1]
            else:
                tri_r6 = self.triangles[tri_r6].n[2]
                first_done = True
        # Find triangle 7 from tri_r7.
        first_done = False
        while self.triangles[tri_r7].v[2] is not None:
            if first_done:
                tri_r7 = self.triangles[tri_r7].n[2]
            else:
                tri_r7 = self.triangles[tri_r7].n[1]
                first_done = True
        return tri_l2, tri_l3, tri_r6, tri_r7

    def __divide_and_conquer(self, begin: int, end: int) -> Tuple[int, int, int, int]:
        """Recursive method for delaunay triangulation.

        Note:
            The assumption is made upon entering this method that the vertices in the range are sorted x, y
            lexicographic.

        Args:
            begin: The beginning of the range of vertices to triangulate (inclusive).
            end: The end of the range of vertices to triangulate (exclusive).

        Returns:
            Triangles 2, 3, 6, and 7 of the triangulation.
        """
        # TODO: Handle horizontal and alternating cuts.
        # NOTE: This requires the following steps:
        # NOTE: - Altering __trivial_triangulation such that it returns the triangle indexes needed for horizontal cuts.
        # NOTE: - Altering __find_ghosts so that it finds those triangles as well.
        # NOTE: - Altering the return signature of this method so that it returns those triangle indices.
        # NOTE: - Adding a parameter for this method that is the axis to cut along, and if it should alternate or not.
        # NOTE: - Calling __divide_and_conquer recursively in this method with the appropriate axis depending on the
        # NOTE:   axis of this cut and if alternating or not.
        # NOTE: - Accept the expanded return values from the recursive __divide_and_conquer calls here.
        # NOTE: - Only for alternating cuts: change __sort so that it sorts the points appropriately to accommodate
        # NOTE:   alternating cuts.
        # TODO: Make the merge algorithm to call here dynamic.
        # NOTE: A simple if condition should suffice I think.
        # Handle base cases.
        if end - begin < 4:
            return self.__trivial_triangulation(begin, end)
        divider = ((end - begin) >> 1) + begin

        # Solve the left half recursively.
        print('NOW RECURSIVELY TRIANGULATING {} THROUGH {}'.format(begin, divider))
        tri_l2, tri_l3, tri_l6, tri_l7 = self.__divide_and_conquer(begin, divider)
        # FIXME: Get rid of draws when debugging not necessary.
        print('RECURSIVELY TRIANGULATED {} THROUGH {}'.format(begin, divider))
        self.draw(order=self.order)
        # self.debug_print()

        # Solve the right half recursively.
        print('NOW  RECURSIVELY TRIANGULATING {} THROUGH {}'.format(divider, end))
        tri_r2, tri_r3, tri_r6, tri_r7 = self.__divide_and_conquer(divider, end)
        # FIXME: Get rid of draws when debugging not necessary.
        print('RECURSIVELY TRIANGULATED {} THROUGH {}'.format(divider, end))
        self.draw(order=self.order)
        # self.debug_print()

        # Merge.
        print('NOW MERGING {} THROUGH {}'.format(begin, end))
        self.__merge_arbitrary(tri_l6, tri_l7, tri_r2, tri_r3)
        # FIXME: Get rid of draws when debugging not necessary.
        # self.draw(order=self.order)
        # self.debug_print()

        return self.__find_ghosts(tri_l2, tri_l3, tri_r6, tri_r7)

    def enforce_delaunay(self) -> None:
        """The flip algorithm. Repeatedly flips edges that are not locally Delaunay until the entire triangulation is
        Delaunay.

        Note:
            The vertices must already be triangulated. Otherwise this method is a no-op (if no triangles exist) or
            undefined (if triangles exist but do not represent a complete triangulation of the vertices).
        """
        # TODO: Test the timing of this algorithm under various conditions to see which is, in practice, more efficient.
        # NOTE: The conditions are as follows:
        # NOTE: - pop() and popleft() when we pull from the edge queue. pop() looks like it does less flips than
        # NOTE:   popleft()?
        # NOTE: - The order that we add edges to the queue. I think pop() only looks like it does less flips because of
        # NOTE:   the order we add to the queue. It might be ideal, when transferring this to C/C++, to use a stack
        # NOTE:   rather than a FIFO queue, so it would be good if we could make that efficient.
        edge_set = set()  # type: Set[Tuple[int, int]]
        edge_queue = collections.deque()  # type: Deque[Tuple[Tuple[int, int], int, int]]

        # Add every edge in the triangulation to the queue.
        for t_i, t in enumerate(self.triangles):
            if t.v[2] is None:
                continue
            for n_i in range(3):
                if self.triangles[t.n[n_i]].v[2] is None:
                    continue
                edge = (t.v[n_i], t.v[(n_i + 1) % 3])
                edge = (min(edge), max(edge))
                if edge in edge_set:
                    continue
                edge_set.add(edge)
                edge_queue.append((edge, t_i, n_i))

        # Flip every edge in the queue.
        while len(edge_queue) > 0:

            # edge: (a, b)
            # t_index_i: The index of triangle i.
            # t_n_index_i: The index in triangle i where edge begins.
            # Pop the next item from the queue (FIFO).
            edge, t_index_i, t_n_index_i = edge_queue.popleft()

            # triangle_i: Triangle i.
            # Do not continue if it is a ghost triangle.
            triangle_i = self.triangles[t_index_i]
            if triangle_i.v[2] is None:
                continue

            # edge_i: The actual edge given the parameters.
            # We use this to check if the edge still exists.
            triangle_i = self.triangles[t_index_i]
            edge_i = (triangle_i.v[t_n_index_i], triangle_i.v[(t_n_index_i + 1) % 3])
            edge_i = (min(edge_i), max(edge_i))
            if edge != edge_i:
                continue

            # t_index_j: The index of triangle j.
            # triangle_j: Triangle j.
            # t_n_index_j: The index in triangle j where the edge begins.
            # We use a loop to find t_n_index_j.
            # This is used to find the vertices and neighbors of triangle j.
            t_index_j = triangle_i.n[t_n_index_i]
            triangle_j = self.triangles[t_index_j]
            t_n_index_j = None
            for j in range(3):
                edge_j = (triangle_j.v[j], triangle_j.v[(j + 1) % 3])
                edge_j = (min(edge_j), max(edge_j))
                if edge_i == edge_j:
                    t_n_index_j = j
                    break
            if t_n_index_j is None:
                raise Exception('Source triangle index missing in neighbor triangle.')

            # Get all vertices and indices we need.
            v_index_i = triangle_i.v[(t_n_index_i + 2) % 3]
            v_index_j = triangle_j.v[(t_n_index_j + 2) % 3]
            vertex_j = self.vertices[v_index_j]

            if self.__in_circle(t_index_i, vertex_j) is Position.INSIDE:
                # At this point, we need to flip.

                # t_index_i1: The index of triangle i's neighbor ccw of triangle j.
                # t_index_i2: The index of triangle i's neighbor cw of triangle j.
                # t_index_j1: The index of triangle j's neighbor ccw of triangle i.
                # t_index_j2: The index of triangle j's neighbor cw of triangle i.
                # Note these are actual indices of the triangles, not in indexes in the neighbor array.
                t_index_i1 = triangle_i.n[(t_n_index_i + 1) % 3]
                t_index_i2 = triangle_i.n[(t_n_index_i + 2) % 3]
                t_index_j1 = triangle_j.n[(t_n_index_j + 1) % 3]
                t_index_j2 = triangle_j.n[(t_n_index_j + 2) % 3]
                triangle_i1 = self.triangles[t_index_i1]
                triangle_i2 = self.triangles[t_index_i2]
                triangle_j1 = self.triangles[t_index_j1]
                triangle_j2 = self.triangles[t_index_j2]

                # Fix triangle i1.
                for i, n in enumerate(triangle_i1.n):
                    if n == t_index_i:
                        triangle_i1.n[i] = t_index_j
                        break

                # Fix triangle j1.
                for i, n in enumerate(triangle_j1.n):
                    if n == t_index_j:
                        triangle_j1.n[i] = t_index_i
                        break

                # Fix triangles i and j.
                # How we fix these triangles depends on the orientation of edge.
                triangle_i.n = [t_index_j, t_index_i2, t_index_j1]
                triangle_j.n = [t_index_i, t_index_j2, t_index_i1]
                if triangle_i.v[t_n_index_i] == edge[0]:
                    triangle_i.v = [v_index_j, v_index_i, edge[0]]
                    triangle_j.v = [v_index_i, v_index_j, edge[1]]
                else:
                    triangle_i.v = [v_index_j, v_index_i, edge[1]]
                    triangle_j.v = [v_index_i, v_index_j, edge[0]]

                # We have to push all edges around the new (i, j) to the queue.

                # Add the edge between triangle i and triangle i2 (between i and a/b).
                if triangle_i2.v[2] is not None:
                    edge = (triangle_i.v[1], triangle_i.v[2])
                    edge = (min(edge), max(edge))
                    edge_queue.append((edge, t_index_i, 1))

                # Add the edge between triangle i and triangle j1 (between a/b and j).
                if triangle_j1.v[2] is not None:
                    edge = (triangle_i.v[0], triangle_i.v[2])
                    edge = (min(edge), max(edge))
                    edge_queue.append((edge, t_index_i, 2))

                # Add the edge between triangle j and triangle j2 (between j and a/b).
                if triangle_j2.v[2] is not None:
                    edge = (triangle_j.v[1], triangle_j.v[2])
                    edge = (min(edge), max(edge))
                    edge_queue.append((edge, t_index_j, 1))

                # Add the edge between triangle j and triangle i1 (between a/b and i).
                if triangle_i1.v[2] is not None:
                    edge = (triangle_j.v[0], triangle_j.v[2])
                    edge = (min(edge), max(edge))
                    edge_queue.append((edge, t_index_j, 2))

                # FIXME: Get rid of draws when debugging not necessary.
                self.draw()
