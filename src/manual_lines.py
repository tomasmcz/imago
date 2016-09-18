"""Computing the grid"""

import unittest
from math import sqrt, acos, copysign
from geometry import l2ad, line, intersection

def lines(corners):
    # TODO Error on triangle 
    corners.sort() # TODO does this help?
    # TODO refactor this vvv
    cor_d = [(corners[0], (c[0] - corners[0][0], c[1] - corners[0][1]), c) for c in
             corners[1:]]
    cor_d = [(float(a[0] * b[0] + a[1] * b[1]) / (sqrt(a[0] ** 2 + a[1] ** 2) *
              sqrt(b[0] **2 + b[1] ** 2)), a[0] * b[1] - b[0] * a[1], c) for a, b, c in cor_d]
    cor_d = sorted([(copysign(acos(min(a, 1)), b), c) for a, b, c in cor_d])
    corners = [corners[0]] + [c for _, c in cor_d]
    return (_lines(corners, 0) + 
            [(corners[0], corners[3]), (corners[1], corners[2])],
            _lines(corners[1:4] + [corners[0]], 0) + 
            [(corners[0], corners[1]), (corners[2], corners[3])])

def _lines(corners, n):
    # TODO what is this?
    if n == 0:
        x = half_line(corners)
        return (_lines([corners[0], x[0], x[1], corners[3]], 1) + [x] + 
                _lines([x[0], corners[1], corners[2], x[1]], 1))
    else:
        x = half_line(corners)
        c = intersection(line(x[0], corners[2]), line(corners[1], corners[3]))
        d = intersection(line(corners[0], corners[3]), line(corners[1], corners[2]))
        if d:
            l = (intersection(line(corners[0], corners[1]), line(c, d)),
                 intersection(line(corners[2], corners[3]), line(c, d)))
        else:
            lx = line(c, (c[0] + corners[0][0] - corners[3][0], 
                      c[1] + corners[0][1] - corners[3][1]))
            l = (intersection(line(corners[0], corners[1]), lx),
                 intersection(line(corners[2], corners[3]), lx))
        l2 = half_line([corners[0], l[0], l[1], corners[3]])
        if n == 1:
            return ([l, l2] + _lines([l[0], l2[0], l2[1], l[1]], 2)
                    + _lines([corners[0], l2[0], l2[1], corners[3]], 2)
                    + _lines([l[0], corners[1], corners[2], l[1]], 2))
        if n == 2:
            return [l, l2]


def half_line(corners):
    """Divides a quadrilateral in half.

    The argument `corners` is a list of four points (tuples of (x, y)),
    representing the corners of a quadrilateral.  The list may start
    on any of the four corners, but must go around the quadrilateral in
    clockwise or counter-clockwise order; skipping around is not allowed.

    The function returns a line (a list of two points) that joins the
    midpoints of two oposite sides of the quadrilateral defined by the
    four passed-in corners.  Arbitrarily, the bisected sides are the
    one joining corner 0 and corner 1, and the one joining corner 2 and
    corner 3."""

    c = center(corners)
    d = intersection(line(corners[0], corners[3]), line(corners[1], corners[2]))
    if d:
        l = line(c, d)
    else:
        l = line(c, (c[0] + corners[0][0] - corners[3][0], 
                     c[1] + corners[0][1] - corners[3][1]))
    p1 = intersection(l, line(corners[0], corners[1]))
    p2 = intersection(l, line(corners[2], corners[3]))
    return (p1, p2)

def center(corners):
    """Given a list of four corner points, return the center of the square."""
    return intersection(line(corners[0], corners[2]), 
                        line(corners[1], corners[3]))


#
# Just tests below here.
#

class test_manual_lines(unittest.TestCase):
    def test_half_line(self):

        """This function tests the half_line() function.  It passes
        in corner-tuples for a bunch of different quadrilaterals and
        verifies that the returned half-line is the expected one."""

        # square
        corners = (
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 10)
        )
        r = half_line(corners)
        assert(r == ((5, 0), (5, 10)))

        # parallelogram leaning right
        corners = (
            (0, 0),
            (10, 0),
            (20, 10),
            (10, 10)
        )
        r = half_line(corners)
        assert(r == ((5, 0), (15, 10)))

        # parallelogram leaning up
        corners = (
            (0, 0),
            (10, 10),
            (10, 20),
            (0, 10)
        )
        r = half_line(corners)
        assert(r == ((5, 5), (5, 15)))

        # isosceles trapezoid, pinched at top
        corners = (
            (0, 0),
            (10, 0),
            (8, 10),
            (2, 10)
        )
        r = half_line(corners)
        assert(r == ((5, 0), (5, 10)))

        # isosceles trapezoid, pinched at bottom
        corners = (
            (2, 0),
            (8, 0),
            (10, 10),
            (0, 10)
        )
        r = half_line(corners)
        assert(r == ((5, 0), (5, 10)))

        # isosceles trapezoid, pinched at right
        corners = (
            (0, 0),
            (10, 2),
            (10, 8),
            (0, 10)
        )
        r = half_line(corners)
        assert(r == ((6, 1), (6, 9)))

        # isosceles trapezoid, pinched at left
        corners = (
            (0, 2),
            (10, 0),
            (10, 10),
            (0, 8)
        )
        r = half_line(corners)
        assert(r == ((4, 1), (4, 9)))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(test_manual_lines)
    unittest.TextTestRunner(verbosity=2).run(suite)
