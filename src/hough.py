"""Hough transform module."""

from math import pi

from PIL import Image

import pcf

class Hough:
    """Hough transform.

    This class stores the parameters of the transformation.
    """
    def __init__(self, size, dt, init_angle):
        self.size = size # this is a tuple (width, height)
        self.dt = dt     # this is the angle step in hough transform
        self.initial_angle = init_angle

    @classmethod
    def default(cls, image):
        """Default parameters for Hough transform of the *image*."""
        size = image.size
        dt = pi / size[1]
        initial_angle = (pi / 4) + (dt / 2)
        return cls(size, dt, initial_angle)

    def transform(self, image):
        image_s = pcf.hough(self.size, image.tobytes(), self.initial_angle,
                            self.dt)
        image_t = Image.frombytes('L', self.size, image_s)
        return image_t

    def apply_filter(self, filter_f):
        return Hough(self.size, self.dt, self.initial_angle,
                     filter_f(self.image))

    def lines_from_list(self, p_list):
        """Take a list of transformed points and return a list of corresponding
        lines as (angle, distance) tuples."""
        # TODO! why is distance allways integer?
        lines = []
        for p in p_list:
            lines.append(self.angle_distance(p))
        return lines

    def all_lines_h(self, image):
        # TODO what is this?
        im_l = image.load()
        lines1 = []
        for x in xrange(self.size[0] / 2):
            for y in xrange(self.size[1]):
                if im_l[x, y]:
                    lines1.append(self.angle_distance((x, y)))
        lines2 = []
        for x in xrange(self.size[0] / 2, self.size[0]):
            for y in xrange(self.size[1]):
                if im_l[x, y]:
                    lines2.append(self.angle_distance((x, y)))
        return [lines1, lines2]

    def all_lines(self):
        # TODO what is this? how does it differ from the upper one?
        im_l = self.image.load()
        lines = []
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                if im_l[x, y]:
                    lines.append(self.angle_distance((x, y)))
        return lines
    
    def angle_distance(self, point):
        """Take a point from the transformed image and return the corresponding
        line in the original as (angle, distance) tuple."""
        return (self.dt * point[1] + self.initial_angle,
                point[0] - self.size[0] / 2)
        
