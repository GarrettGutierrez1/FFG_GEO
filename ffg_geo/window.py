# -*- coding: utf-8 -*-
"""window.py

A module implementing the Window class, which allows drawing and the saving of images and video.

License:
    http://www.apache.org/licenses/LICENSE-2.0"""

import enum
import os
import pathlib
from typing import Any, Tuple

import cv2
import numpy as np


# noinspection PyUnresolvedReferences
class LineType(enum.Enum):
    FILLED = cv2.FILLED
    LINE_4 = cv2.LINE_4
    LINE_8 = cv2.LINE_8
    LINE_AA = cv2.LINE_AA


class Window(object):
    """A class for rendering and displaying primitives."""
    def __init__(self, window_name: str, dim: Tuple[int, int],
                 color: Tuple[float, float, float] = (255.0, 255.0, 255.0), resizeable: bool = False,
                 image_dir: str = 'results_images', video_dir: str = 'results_videos') -> None:
        """Initializes the window. Does not create the actual cv2 window.

        Note:
            By default, the coordinate system for all draws will be such that the upper-left is (0, 0) and the bottom-
            right is (dim[0], dim[1]). This can be altered using other methods after initialization.

        Args:
            window_name: The name of the window.
            dim: The dimensions of the screen in pixels.
            color: The bgr color of the window background.
            resizeable: If the window should be resizeable.
            image_dir: The directory to save images in.
            video_dir: The directory to save videos in.
        """
        if dim[0] < 1:
            dim = (1, dim[1])
        if dim[1] < 1:
            dim = (dim[0], 1)
        self.__dim = dim
        self.__left = 0.0
        self.__right = float(self.__dim[0])
        self.__top = 0.0
        self.__bottom = float(self.__dim[1])
        self.__color = color
        # noinspection PyUnresolvedReferences
        self.__screen = np.zeros((self.__dim[1], self.__dim[0], 3), np.uint8)
        self.__screen[:] = self.__color
        self.__window_created = False
        self.__window_name = window_name
        self.__window_title = window_name
        if resizeable:
            # noinspection PyUnresolvedReferences
            self.__window_flag = cv2.WINDOW_NORMAL
        else:
            # noinspection PyUnresolvedReferences
            self.__window_flag = cv2.WINDOW_AUTOSIZE
        self.__image_dir = image_dir
        self.__video_dir = video_dir
        self.__image_count = 0
        pathlib.Path(self.__image_dir).mkdir(parents=False, exist_ok=True)
        pathlib.Path(self.__video_dir).mkdir(parents=False, exist_ok=True)
        self.flush_images()

    def flush_images(self) -> None:
        """Deletes all images in the image directory."""
        filenames = [filename for filename in os.listdir(self.__image_dir) if filename.endswith('.png')]
        for filename in filenames:
            os.remove(os.path.join(self.__image_dir, filename))
        self.__image_count = 0

    def flush(self) -> None:
        """Refills the screen with the background color."""
        self.__screen[:] = self.__color

    def set_title(self, window_title: str) -> None:
        """Sets the title of the window.

        Args:
            window_title: The new title of the window.
        """
        self.__window_title = window_title
        if self.__window_created:
            # noinspection PyUnresolvedReferences
            cv2.setWindowTitle(self.__window_name, self.__window_title)

    def display(self, ms: int = 50) -> int:
        """Displays the window.

        Args:
            ms: The number of milliseconds to display. 0 means infinitely, until a key is pressed.

        Returns:
            The value of the key event (when ms is 0).
        """
        # Create the window if it has not already been created.
        if not self.__window_created:
            # noinspection PyUnresolvedReferences
            cv2.namedWindow(self.__window_name, self.__window_flag)
            # noinspection PyUnresolvedReferences
            cv2.setWindowProperty(self.__window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
            # noinspection PyUnresolvedReferences
            cv2.setWindowTitle(self.__window_name, self.__window_title)
            self.__window_created = True
        # noinspection PyUnresolvedReferences
        cv2.imshow(self.__window_name, self.__screen)
        # noinspection PyUnresolvedReferences
        return cv2.waitKey(ms)

    def save_image(self) -> None:
        """Saves an image in the save_dir with the filename 'image-#.pgn' where # is the image's index."""
        filename = '{}/image-{}.png'.format(self.__image_dir, str(self.__image_count).zfill(6))
        print('TAKING SCREENSHOT {}'.format(filename))
        # noinspection PyUnresolvedReferences
        cv2.imwrite(filename, self.__screen)
        self.__image_count += 1

    def save_video(self, filename: str = 'video', fps: float = 20) -> None:
        """Saves a video from the images saved.

        Args:
            filename: The filename to save the video with. Note: should not include extension.
            fps: The frames per second.
        """
        filename = '{}.avi'.format(filename)
        filename = os.path.join(self.__video_dir, filename)
        image_names = [filename_ for filename_ in os.listdir(self.__image_dir) if filename_.endswith('.png')]
        if len(image_names) < 1:
            return
        # noinspection PyUnresolvedReferences
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        # noinspection PyUnresolvedReferences
        video = cv2.VideoWriter(filename, fourcc, fps, self.__dim)
        for filename in image_names:
            # noinspection PyUnresolvedReferences
            video.write(cv2.imread(os.path.join(self.__image_dir, filename)))

    def set_coordinate_system(self, left: float, right: float, top: float, bottom: float) -> None:
        """Sets the coordinate system, maintaining the aspect ratio.

        Args:
            left: The left most x-coordinate to fit on the screen.
            right: The right most x-coordinate to fit on the screen.
            top: The top most y-coordinate to fit onto the screen.
            bottom: The bottom most y-coordinate to fit onto the screen.
        """
        y_to_x_ratio_screen = self.__dim[1] / self.__dim[0]
        x_span = abs(left - right)
        y_span = abs(top - bottom)
        y_to_x_ratio_world = y_span / x_span
        if y_to_x_ratio_world <= y_to_x_ratio_screen:
            # We can fit by padding on the y-axis.
            y_center = (top + bottom) * 0.5
            y_adjustment = y_to_x_ratio_screen / y_to_x_ratio_world
            # Top.
            top_off_center = top - y_center
            top_new_off_center = top_off_center * y_adjustment
            top = top_new_off_center + y_center
            # Bottom.
            bottom_off_center = bottom - y_center
            bottom_new_off_center = bottom_off_center * y_adjustment
            bottom = bottom_new_off_center + y_center
        else:
            # We can fit by padding on the x-axis.
            x_to_y_ratio_screen = self.__dim[0] / self.__dim[1]
            x_to_y_ratio_world = x_span / y_span
            x_center = (left + right) * 0.5
            x_adjustment = x_to_y_ratio_screen / x_to_y_ratio_world
            # Left.
            left_off_center = left - x_center
            left_new_off_center = left_off_center * x_adjustment
            left = left_new_off_center + x_center
            # Right.
            right_off_center = right - x_center
            right_new_off_center = right_off_center * x_adjustment
            right = right_new_off_center + x_center
        self.set_coordinate_system_naive(left, right, top, bottom)

    def set_coordinate_system_naive(self, left: float, right: float, top: float, bottom: float) -> None:
        """Sets the coordinate system naively. Naive in this sense means that aspect ratio is not maintained.

        Example:
            If the Window was initialized with screen dimensions (800, 600), and this method is called with parameters
            0, 100, 0, 600, the window screen will remain (800, 600) pixels in dimensions but horizontal lines going
            from left to right will be 100 units and 800 pixels long (a 1:8 ratio) while vertical lines going from top
            to bottom will be 600 units and 600 pixels long (a 1:1 ratio).

        Args:
            left: The x-coordinate at the very left of the screen.
            right: The x-coordinate at the very right of the screen.
            top: The y-coordinate at the very top of the screen.
            bottom: The y-coordinate at the very bottom of the screen.
        """
        self.__left = left
        self.__right = right
        self.__top = top
        self.__bottom = bottom

    def __get_screen_point(self, p: Any) -> Tuple[int, int]:
        """Given a point in world coordinates, return the point in screen coordinates.

        Note:
            p must be of a type such that the x- and y-coordinates are accessible using the [] operator with keys 0 and
            1 respectively.

        Args:
            p: A point in world coordinates.

        Returns:
            A point in screen coordinates.
        """
        # x_distance is the percentage of the way that the point is from the left to the right.
        # y_distance is the same except from the top to the bottom.
        x_distance = (p[0] - self.__left) / (self.__right - self.__left)
        y_distance = (p[1] - self.__top) / (self.__bottom - self.__top)
        # x_value and y_values are the actual screen coordinates casted into ints so that the point lies directly on an
        # actual pixel.
        x_value = int(x_distance * self.__dim[0])
        y_value = int(y_distance * self.__dim[1])
        return x_value, y_value

    def draw_line(self, pt1: Any, pt2: Any, color: Tuple[float, float, float], thickness: int = 1,
                  line_type: LineType = LineType.LINE_AA) -> None:
        """Draws a line.

        Note:
            Points pt1 and pt2 must be of a type such that the x- and y-coordinates are accessible using the [] operator
            with keys 0 and 1 respectively.

        Note:
            A thickness > 1 is required for LineType.FILLED.

        Args:
            pt1: The source point of the line in world coordinates.
            pt2: The destination point of the line in world coordinates.
            color: The BGR color of the line.
            thickness: The thickness of the line in pixels.
            line_type: The type of line.
        """
        pt1 = self.__get_screen_point(pt1)
        pt2 = self.__get_screen_point(pt2)
        # noinspection PyUnresolvedReferences
        cv2.line(img=self.__screen, pt1=pt1, pt2=pt2, color=color, thickness=thickness, lineType=line_type.value)

    def draw_circle(self, center: Any, radius: int, color: Tuple[float, float, float], thickness: int = 1,
                    line_type: LineType = LineType.LINE_AA) -> None:
        """Draws a circle.

        Note:
            Center must be of a type such that the x- and y-coordinates are accessible using the [] operator with keys 0
            and 1 respectively.

        Note:
            A thickness > 1 is required for LineType.FILLED.

        Args:
            center: The center of the circle in world coordinates.
            radius: The radius of the circle in pixels (NOT WORLD COORDINATES).
            color: The BGR color of the circle.
            thickness: The thickness of the circle in pixels.
            line_type: The type of line.
        """
        center = self.__get_screen_point(center)
        # noinspection PyUnresolvedReferences
        cv2.circle(img=self.__screen, center=center, radius=radius, color=color, thickness=thickness,
                   lineType=line_type.value)

    def draw_cross(self, center: Any, color: Tuple[float, float, float], length: int, thickness: int = 1,
                   line_type: LineType = LineType.LINE_AA) -> None:
        """Draws a cross.

        Note:
            Center must be of a type such that the x- and y-coordinates are accessible using the [] operator with keys 0
            and 1 respectively.

        Note:
            A thickness > 1 is required for LineType.FILLED.

        Args:
            center: The center of the cross in world coordinates.
            color: The BGR color of the cross.
            length: The length of the arms of the cross in pixels (NOT WORLD COORDINATES).
            thickness: The thickness of the arms of the cross in pixels.
            line_type: The type of line.
        """
        center = self.__get_screen_point(center)
        left = (center[0] - length, center[1])
        right = (center[0] + length, center[1])
        top = (center[0], center[1] - length)
        bottom = (center[0], center[1] + length)
        # noinspection PyUnresolvedReferences
        cv2.line(img=self.__screen, pt1=left, pt2=right, color=color, thickness=thickness, lineType=line_type.value)
        # noinspection PyUnresolvedReferences
        cv2.line(img=self.__screen, pt1=top, pt2=bottom, color=color, thickness=thickness, lineType=line_type.value)
