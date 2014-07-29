"""Imago grid fitting module

RANSAC inspired method.
"""

import random
from math import sqrt

from intrsc import intersections_from_angl_dist
import linef
import params
import ransac
import manual_lines as manual
from geometry import l2ad

# TODO comments, refactoring, move methods to appropriate modules

class GridFittingFailedError(Exception):
    pass

class BadGenError(Exception):
    pass

def plot_line(line, c, size):
    """Plot a *line* with pyplot."""
    points = linef.line_from_angl_dist(line, size)
    pyplot.plot(*zip(*points), color=c)

class Diagonal_model:
    """Ransac model for finding diagonals."""
    def __init__(self, data):
        self.data = [p for p in sum(data, []) if p]
        self.lines = data
        self.gen = self.initial_g()

    def initial_g(self):
        l1, l2 = random.sample(self.lines, 2)
        for i in xrange(len(l1)):
            for j in xrange(len(l2)):
                if i == j:
                    continue
                if l1[i] and l2[j]:
                    yield (l1[i], l2[j])

    def remove(self, data):
        self.data = list(set(self.data) - set(data))

    def initial(self):
        try:
            nxt = self.gen.next()
        except StopIteration:
            self.gen = self.initial_g()
            nxt = self.gen.next()
        return nxt

    def get(self, sample):
        if len(sample) == 2:
            return ransac.points_to_line(*sample)
        else:
            return ransac.least_squares(sample)

    def score(self, est, dist):
        cons = []
        score = 0
        a, b, c = est
        dst = lambda (x, y): abs(a * x + b * y + c) / sqrt(a*a+b*b)
        l1 = None
        l2 = None
        for p in self.data:
            d = dst(p)
            if d <= dist:
                cons.append(p)
                if p.l1 == l1 or p.l2 == l2:
                    return float("inf"), []
                else:
                    l1, l2 = p.l1, p.l2
            else: # TODO delete this or refactor
                score += min(d, dist)

        return score, cons

def intersection((a1, b1, c1), (a2, b2, c2)):
    """Intersection of two lines, given by coefficients in their equations."""
    delim = float(a1 * b2 - b1 * a2)
    if delim == 0:
        return None
    x = (b1 * c2 - c1 * b2) / delim
    y = (c1 * a2 - a1 * c2) / delim
    return x, y

class Point:
    """Class that represents a point in 2D."""
    def __init__(self, (x, y)):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self):
        return 2

    def to_tuple(self):
        return (self.x, self.y)

class Line:
    """Line with a list of important points that lie on it.

    This and the Point class in this module serves to implement a model of
    perspective plain -- a line has a list of intersections with other lines and
    each intersection has two lines that go through it.
    """

    def __init__(self, (a, b, c)):
        self.a, self.b, self.c = (a, b, c)
        self.points = []

    @classmethod
    def from_ad(cls, (a, d), size):
        p = linef.line_from_angl_dist((a, d), size)
        return cls(ransac.points_to_line(*p))

    def __iter__(self):
        yield self.a
        yield self.b
        yield self.c

    def __len__(self):
        return 3

    def __getitem__(self, key):
        if key == 0:
            return self.a
        elif key == 1:
            return self.b
        elif key == 2:
            return self.c

def gen_corners(d1, d2, min_size):
    """Generate candidates on corner positions from the diagonals."""
    for c1 in d1.points:
        if c1 in d2.points:
            continue
        pass
        try:
            c2 = [p for p in d2.points if p in c1.l1.points][0]
            c3 = [p for p in d1.points if p in c2.l2.points][0]
            c4 = [p for p in d2.points if p in c3.l1.points][0]
            x_min = min([c1[0], c2[0], c3[0], c4[0]])
            x_max = max([c1[0], c2[0], c3[0], c4[0]])
            if x_max - x_min < min_size:
                continue
            y_min = min([c1[1], c2[1], c3[1], c4[1]])
            y_max = max([c1[1], c2[1], c3[1], c4[1]])
            if y_max - y_min < min_size:
                continue

        except IndexError:
            continue
            # there is not a corresponding intersection
            # TODO create an intersection?
        try:
            yield manual.lines(map(lambda p: p.to_tuple(), [c2, c1, c3, c4]))
        except (TypeError):
            pass
            # the square was too small to fit 17 lines inside
            # TODO define SquareTooSmallError or something

def dst(p, l):
    """Distance from a point to a line."""
    (x, y), (a, b, c) = p, ransac.points_to_line(*l)
    return abs(a * x + b * y + c) / sqrt(a*a+b*b)

def score(lines, points):
    # TODO find whether the point actualy lies on the line or just in the same
    # direction
    score = 0
    for p in points:
        s = min(map(lambda l: dst(p, l), lines))
        s = min(s, 2)
        score += s
    return score


def find(lines, size, l1, l2, bounds, hough, show_all, do_something, logger):
    """Find the best grid given the *lines* and *size* of the image.
    
    Last three parameters serves for debugging, *l1*, *l2*, *bounds* and *hough*
    are here for compatibility with older version of gridf, so they can be
    easily exchanged, tested and compared.
    """

    new_lines1 = map(lambda l: Line.from_ad(l, size), lines[0])
    new_lines2 = map(lambda l: Line.from_ad(l, size), lines[1])
    for l1 in new_lines1:
        for l2 in new_lines2:
            p = Point(intersection(l1, l2))
            p.l1 = l1
            p.l2 = l2
            l1.points.append(p)
            l2.points.append(p)

    points = [l.points for l in new_lines1]

    def dst_p(x, y):
        x = x - size[0] / 2
        y = y - size[1] / 2
        return sqrt(x * x + y * y)

    for n_tries in xrange(3):
        logger("finding the diagonals")
        model = Diagonal_model(points)
        diag_lines = ransac.ransac_multi(6, points, 2,
                                         params.ransac_diagonal_iter, model=model)
        diag_lines = [l[0] for l in diag_lines]
        centers = []
        cen_lin = []
        for i in xrange(len(diag_lines)):
            line1 = diag_lines[i]
            for line2 in diag_lines[i+1:]:
                c = intersection(line1, line2)
                if c and dst_p(*c) < min(size) / 2:
                    cen_lin.append((line1, line2, c))
                    centers.append(c)

        if show_all:
            import matplotlib.pyplot as pyplot
            from PIL import Image

            def plot_line_g((a, b, c), max_x):
                find_y = lambda x: - (c + a * x) / b
                pyplot.plot([0, max_x], [find_y(0), find_y(max_x)], color='b')

            fig = pyplot.figure(figsize=(8, 6))
            for l in diag_lines:
                plot_line_g(l, size[0])
            pyplot.scatter(*zip(*sum(points, [])))
            if len(centers) >= 1:
                pyplot.scatter([c[0] for c in centers], [c[1] for c in centers], color='r')
            pyplot.xlim(0, size[0])
            pyplot.ylim(0, size[1])
            pyplot.gca().invert_yaxis()
            fig.canvas.draw()
            size_f = fig.canvas.get_width_height()
            buff = fig.canvas.tostring_rgb()
            image_p = Image.fromstring('RGB', size_f, buff, 'raw')
            do_something(image_p, "finding diagonals")

        logger("finding the grid")
        data = sum(points, [])
        # TODO what if lines are missing?
        sc = float("inf")
        grid = None
        for (line1, line2, c) in cen_lin:
            diag1 = Line(line1)
            diag1.points = ransac.filter_near(data, diag1, 2)
            diag2 = Line(line2)
            diag2.points = ransac.filter_near(data, diag2, 2)


            grids = list(gen_corners(diag1, diag2, min(size) / 3))
            
            try:
                new_sc, new_grid = min(map(lambda g: (score(sum(g, []), data), g), grids))
                if new_sc < sc:
                    sc, grid = new_sc, new_grid
            except ValueError:
                pass
        if grid:
            break
    else:
        raise GridFittingFailedError
        
    grid_lines = [[l2ad(l, size) for l in grid[0]], 
                  [l2ad(l, size) for l in grid[1]]]
    grid_lines[0].sort(key=lambda l: l[1])
    grid_lines[1].sort(key=lambda l: l[1])
    if grid_lines[0][0][0] > grid_lines[1][0][0]:
        grid_lines = grid_lines[1], grid_lines[0]

    return grid, grid_lines

