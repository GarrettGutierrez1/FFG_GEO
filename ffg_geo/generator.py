# -*- coding: utf-8 -*-
"""generator.py

A module for generating lists of Vector2s. These can be generated randomly within a square, within a rectangle, within a
circle, withing an ellipse, or on an axis. They can also be generated as vertices distributed uniformly on a grid, but
this method is not random.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import random
from typing import List, Tuple

from ffg_geo.vector2 import Vector2


class Generator:
    """A random Vector2 generator."""
    @staticmethod
    def seed(a: int = 0) -> None:
        """Seeds the generator.

        Args:
            a: The seed."""
        random.seed(a)

    @staticmethod
    def __make_square(x_min: float, x_max: float, y_min: float, y_max: float) -> Tuple[float, float, float, float]:
        """Returns the input parameters adjusted such that the region defined by the output parameters is the largest
        square contained in and centered on the region defined by the input parameters.

        Args:
            x_min: The minimum x value of the rectangular region.
            x_max: The maximum x value of the rectangular region.
            y_min: The minimum y value of the rectangular region.
            y_max: The maximum y value of the rectangular region.

        Returns:
            The x_min, x_max, y_min, y_max of the resulting square region."""
        x_width = x_max - x_min
        y_height = y_max - y_min
        x_center = (x_min + x_max) * 0.5
        y_center = (y_min + y_max) * 0.5
        r_min = min(x_width, y_height) * 0.5
        return x_center - r_min, x_center + r_min, y_center - r_min, y_center + r_min

    @staticmethod
    def in_square(n: int, x_min: float, x_max: float, y_min: float, y_max: float) -> List[Vector2]:
        """Generates random Vector2s within a square.

        Args:
            n: The number of Vector2s to randomly generate.
            x_min: The minimum x value of the square.
            x_max: The maximum x value of the square.
            y_min: The minimum y value of the square.
            y_max: The maximum y value of the square.

        Returns:
            A list of Vector2s."""
        x_min, x_max, y_min, y_max = Generator.__make_square(x_min, x_max, y_min, y_max)
        return Generator.in_rect(n, x_min, x_max, y_min, y_max)

    @staticmethod
    def in_rect(n: int, x_min: float, x_max: float, y_min: float, y_max: float) -> List[Vector2]:
        """Generates random Vector2s within a rectangle.

        Args:
            n: The number of Vector2s to randomly generate.
            x_min: The minimum x value of the rectangle.
            x_max: The maximum x value of the rectangle.
            y_min: The minimum y value of the rectangle.
            y_max: The maximum y value of the rectangle.

        Returns:
            A list of Vector2s."""
        result = []
        while len(result) < n:
            v = Vector2(random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            result.append(v)
        return result

    @staticmethod
    def in_circle(n: int, x_min: float, x_max: float, y_min: float, y_max: float) -> List[Vector2]:
        """Generates random Vector2s within a circle.

        Args:
            n: The number of Vector2s to randomly generate.
            x_min: The minimum x value of the circle.
            x_max: The maximum x value of the circle.
            y_min: The minimum y value of the circle.
            y_max: The maximum y value of the circle.

        Returns:
            A list of Vector2s."""
        x_min, x_max, y_min, y_max = Generator.__make_square(x_min, x_max, y_min, y_max)
        return Generator.in_ellipse(n, x_min, x_max, y_min, y_max)

    @staticmethod
    def in_ellipse(n: int, x_min: float, x_max: float, y_min: float, y_max: float) -> List[Vector2]:
        """Generates random Vector2s within an ellipse.

        Args:
            n: The number of Vector2s to randomly generate.
            x_min: The minimum x value of the ellipse.
            x_max: The maximum x value of the ellipse.
            y_min: The minimum y value of the ellipse.
            y_max: The maximum y value of the ellipse.

        Returns:
            A list of Vector2s."""
        result = []
        r_x = abs(x_max - x_min) * 0.5
        r_y = abs(y_max - y_min) * 0.5
        x_center = (x_min + x_max) * 0.5
        y_center = (y_min + y_max) * 0.5
        while len(result) < n:
            v = Vector2(random.uniform(x_min, x_max), random.uniform(y_min, y_max))
            if (((v[0] - x_center) ** 2) / (r_x ** 2)) + (((v[1] - y_center) ** 2) / (r_y ** 2)) > 1.0:
                continue
            result.append(v)
        return result

    @staticmethod
    def on_axis(n: int, v_axis_min: float, v_axis_max: float, c_axis_val: float, v_axis: int,
                uniform: bool) -> List[Vector2]:
        """Generate random Vector2's on an axis.

        Args:
            n: The number of Vector2s to randomly generate.
            v_axis_min: The minimum value on the variable axis.
            v_axis_max: The maximum value on the variable axis.
            c_axis_val: The value of the constant axis.
            v_axis: The variable axis.
            uniform: If the points should be uniform rather than random.

        Returns:
            A list of Vector2s."""
        result = []
        if uniform:
            v_axis_step = (v_axis_max - v_axis_min) / (n - 1)
            for index in range(n):
                coordinates = [0.0, 0.0]
                coordinates[v_axis] = v_axis_min + (v_axis_step * index)
                coordinates[1 - v_axis] = c_axis_val
                result.append(Vector2(coordinates[0], coordinates[1]))
        else:
            for index in range(n):
                coordinates = [0.0, 0.0]
                coordinates[v_axis] = random.uniform(v_axis_min, v_axis_max)
                coordinates[1 - v_axis] = c_axis_val
                result.append(Vector2(coordinates[0], coordinates[1]))
        return result

    @staticmethod
    def in_regional_cut(n: int, cuts: int, axis: int, alternate: bool, x_min: float, x_max: float, y_min: float,
                        y_max: float, method: str) -> List[Vector2]:
        """Generates random Vector2s by recursively cutting the region into halves and then in the base case generating
        n points per region using the specified method. Can be used to generate points in a more uniform manner.

        Args:
            n: The number of Vector2s to randomly generate per leaf region.
            cuts: The number of recursive divisions to make.
            axis: The axis to cut on initially.
            alternate: If the axis to cut on should alternate in subsequent cuts.
            x_min: The minimum x value of the initial region.
            x_max: The maximum x value of the initial region.
            y_min: The minimum y value of the initial region.
            y_max: The maximum y value of the initial region.
            method: The method to use to generate points at the end of the cuts.

        Returns:
            A list of Vector2s."""
        if cuts < 1:
            if method == 's':
                # Square.
                return Generator.in_square(n, x_min, x_max, y_min, y_max)
            elif method == 'h':
                # Horizontal line.
                return Generator.on_axis(n, x_min, x_max, (y_min + y_max) * 0.5, 0, False)
            elif method == 'v':
                # Vertical line.
                return Generator.on_axis(n, y_min, y_max, (x_min + x_max) * 0.5, 1, False)
            elif method == 'c':
                # Circle.
                return Generator.in_circle(n, x_min, x_max, y_min, y_max)
            elif method == 'e':
                # Ellipse.
                return Generator.in_ellipse(n, x_min, x_max, y_min, y_max)
            elif method == 'o':
                # On exact center.
                x_center = (x_min + x_max) * 0.5
                y_center = (y_min + y_max) * 0.5
                return [Vector2(x_center, y_center) for _ in range(n)]
            else:
                # Rectangle.
                return Generator.in_rect(n, x_min, x_max, y_min, y_max)
        # Determine next axis.
        if alternate:
            n_axis = 1 - axis
        else:
            n_axis = axis
        # Perform recursive cuts.
        if axis == 0:
            # Cut on x axis.
            y_center = (y_min + y_max) * 0.5
            lower = Generator.in_regional_cut(n, cuts - 1, n_axis, alternate, x_min, x_max, y_min, y_center, method)
            upper = Generator.in_regional_cut(n, cuts - 1, n_axis, alternate, x_min, x_max, y_center, y_max, method)
            return lower + upper
        # Cut on y axis.
        x_center = (x_min + x_max) * 0.5
        left = Generator.in_regional_cut(n, cuts - 1, n_axis, alternate, x_min, x_center, y_min, y_max, method)
        right = Generator.in_regional_cut(n, cuts - 1, n_axis, alternate, x_center, x_max, y_min, y_max, method)
        return left + right

    @staticmethod
    def duplicate(vertices: List[Vector2], min_duplicates: int, max_duplicates: int) -> List[Vector2]:
        """
        Given a list of vertices, returns a shuffled list of duplicates of those vertices. A random number of duplicates
        is chosen uniformly between [min_duplicates, max_duplicates] for every vertex independently. Every vertex from
        the source list will appear in the resulting list at least once: the number of duplicates is the total number
        minus 1.

        Args:
            vertices: The vertices to duplicate.
            min_duplicates: The minimum number of duplicates per vertex.
            max_duplicates: The maximum number of duplicates per vertex.

        Returns:
            A shuffled list of duplicate vertices."""
        result = []
        for vertex in vertices:
            num_duplicates = random.randrange(min_duplicates, max_duplicates + 1)
            for _ in range(num_duplicates + 1):
                new_vertex = Vector2(vertex[0], vertex[1])
                result.append(new_vertex)
        random.shuffle(result)
        return result

    @staticmethod
    def in_grid(x_min: float, x_max: float, y_min: float, y_max: float, x_div: int, y_div: int) -> List[Vector2]:
        """Generates axis aligned points in a grid.

        Args:
            x_min: The minimum x value of the region to generate the grid within.
            x_max: The maximum x value of the region to generate the grid within.
            y_min: The minimum y value of the region to generate the grid within.
            y_max: The maximum y value of the region to generate the grid within.
            x_div: The number of horizontal grid lines in the region.
            y_div: The number of vertical grid lines in the region.

        Returns:
            A list of vertices."""
        result = []
        x_div = min(x_div, 1)
        y_div = min(y_div, 1)
        x_step = (x_max - x_min) / x_div
        y_step = (y_max - y_min) / y_div
        for x_factor in range(x_div + 1):
            x = x_step * x_factor + x_min
            for y_factor in range(y_div + 1):
                y = y_step * y_factor + y_min
                result.append(Vector2(x, y))
        return result
