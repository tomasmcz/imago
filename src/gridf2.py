from math import sqrt
import random
import sys

import linef as linef
import gridf as gridf
from manual import lines as g_grid
from geometry import l2ad
import new_geometry as gm


def plot_line(line, c):
    points = linef.line_from_angl_dist(line, (520, 390))
    pyplot.plot(*zip(*points), color=c)

def dst((x, y), (a, b, c)):
    return abs(a * x + b * y + c) / sqrt(a*a+b*b)

def points_to_line((x1, y1), (x2, y2)):
    return (y2 - y1, x1 - x2, x2 * y1 - x1 * y2)

def to_general(line):
    points = linef.line_from_angl_dist(line, (520, 390))
    return points_to_line(*points)

def nearest(lines, point):
    return min(map(lambda l: dst(point, l), lines))

def nearest2(lines, point):
    return min(map(lambda l: dst(point, points_to_line(*l)), lines))


def generate_models(sgrid, lh):
    for f in [0, 1, 2, 3, 5, 7, 8, 11, 15, 17]:
        try:
            grid = gm.fill(sgrid[0], sgrid[1], lh , f)
        except ZeroDivisionError:
            continue
        grid = [sgrid[0]] + grid + [sgrid[1]]
        for s in xrange(17 - f):
            grid = [gm.expand_left(grid, lh)] + grid
        yield grid
        for i in xrange(17 - f):
            grid = grid[1:]
            grid.append(gm.expand_right(grid, lh))
            yield grid

def score(grid, lines, limit):
    dst = lambda (a, b, c): (a * 260 + b * 195 + c) / sqrt(a*a+b*b)
    dsg = lambda l: dst(points_to_line(*l))
    ds = map(dsg, grid)
    d = max(map(abs, ds))
    if d > limit:
        return float("inf")
    score = 0
    for line in lines:
        s = min(map(lambda g: abs(line[1] - g), ds))
        s = min(s, 4)
        score += s

    return score

def lines2grid(lines, perp_l):
    b1, b2 = perp_l[0], perp_l[-1]
    f = lambda l: (gm.intersection(b1, l), gm.intersection(b2, l))
    return map(f, lines)

def pertubations(grid, middle_l):
    corners = [grid[0], grid[-1]]
    for l in [0, 1]:
        for c in [0, 1]:
            for s in [0, 1]:
                for x in [-1, 1]:
                    sgrid = corners
                    sgrid[l] = list(sgrid[l])
                    sgrid[l][c] = list(sgrid[l][c])
                    sgrid[l][c][s] += x
                    try:
                        middle = middle_l(sgrid)
                        lh = (gm.intersection(sgrid[0], middle), gm.intersection(sgrid[1], middle))
                        sgrid = ([sgrid[0]] +
                             gm.fill(sgrid[0], sgrid[1], lh, 17) +
                             [sgrid[1]])
                    except ZeroDivisionError:
                        continue

                    yield sgrid


def test(): 
    import pickle
    import matplotlib.pyplot as pyplot
    import time

    size = (520, 390)
    points = pickle.load(open('edges.pickle'))

    lines = pickle.load(open('lines.pickle'))

    r_lines = pickle.load(open('r_lines.pickle'))

    #pyplot.scatter(*zip(*sum(r_lines, [])))
    #pyplot.show()

    l1, l2 = lines

    lines_general = map(to_general, sum(lines, []))
    near_points = [p for p in points if nearest(lines_general, p) <= 2]

    while True:
        t0 = time.time()
        sc1, gridv = float("inf"), None
        sc2, gridh = float("inf"), None
        sc1_n, sc2_n = float("inf"), float("inf")
        gridv_n, gridh_n = None, None
        for k in range(50):
            for i in range(5):
                l1s = random.sample(l1, 2)
                l1s.sort(key=lambda l: l[1])
                sgrid = map(lambda l:linef.line_from_angl_dist(l, size), l1s)
                middle_l1 = lambda m: ((m, 0),(m, 390))
                middle_l = lambda sgrid: middle_l1(gm.intersection((sgrid[0][0], sgrid[1][1]), 
                                                (sgrid[0][1], sgrid[1][0]))[0])
                middle = middle_l(sgrid)
                lh = (gm.intersection(sgrid[0], middle), gm.intersection(sgrid[1], middle))
                sc1_n, gridv_n = min(map(lambda g: (score(g, l1, 210), g), generate_models(sgrid, lh)))

                p = True
                while p:
                    p = False
                    for ng in pertubations(gridv_n, middle_l): # TODO randomize
                        sc = score(ng, l1, 210)
                        if sc < sc1_n:
                            sc1_n, gridv_n = sc, ng
                            p = True

                if sc1_n < sc1:
                    sc1, gridv = sc1_n, gridv_n

            for i in range(5):
                l2s = random.sample(l2, 2)
                l2s.sort(key=lambda l: l[1])
                sgrid = map(lambda l:linef.line_from_angl_dist(l, size), l2s) 
                middle_l1 = lambda m: ((0, m),(520, m))
                middle_l = lambda sgrid: middle_l1(gm.intersection((sgrid[0][0], sgrid[1][1]), 
                                                (sgrid[0][1], sgrid[1][0]))[1])
                middle = middle_l(sgrid)
                lh = (gm.intersection(sgrid[0], middle), gm.intersection(sgrid[1], middle))
                sc2_n, gridh_n = min(map(lambda g: (score(g, l2, 275), g), generate_models(sgrid, lh)))

                p = True
                while p:
                    p = False
                    for ng in pertubations(gridh_n, middle_l): # TODO randomize
                        sc = score(ng, l2, 275)
                        if sc < sc2_n:
                            sc2_n, gridh = sc, ng
                            p = True

                if sc2_n < sc2:
                    sc2, gridh = sc2_n, gridh_n

            gridv, gridh = lines2grid(gridv, gridh), lines2grid(gridh, gridv)

        print time.time() - t0
        print sc1, sc2

        pyplot.scatter(*zip(*near_points))

        #map(lambda l: plot_line(l, 'g'), l1 + l2)
        map(lambda l: pyplot.plot(*zip(*l), color='g'), gridv)
        map(lambda l: pyplot.plot(*zip(*l), color='g'), gridh)
        #plot_line(l2s[0], 'r')
        #plot_line(l2s[1], 'r')
        #plot_line(l1s[0], 'r')
        #plot_line(l1s[1], 'r')
        pyplot.xlim(0, 520)
        pyplot.ylim(0, 390)
        pyplot.show()

def find(lines, size, l1, l2, bounds, hough, show_all, do_something, logger):
    logger("finding the grid")
    l1, l2 = lines
    sc1, gridv = float("inf"), None
    for i in range(250):
        l1s = random.sample(l1, 2)
        l1s.sort(key=lambda l: l[1])
        sgrid = map(lambda l:linef.line_from_angl_dist(l, size), l1s) 
        middle = lambda m: ((m, 0),(m, size[1]))
        middle = middle(gm.intersection((sgrid[0][0], sgrid[1][1]), 
                                        (sgrid[0][1], sgrid[1][0]))[0])
        lh = (gm.intersection(sgrid[0], middle), gm.intersection(sgrid[1], middle))
        sc1_n, gridv_n = min(map(lambda g: (score(g, l1, size[1] / 2 + 15), g), generate_models(sgrid, lh)))
        if sc1_n < sc1:
            sc1, gridv = sc1_n, gridv_n

    sc2, gridh = float("inf"), None
    for i in range(250):
        l2s = random.sample(l2, 2)
        l2s.sort(key=lambda l: l[1])
        sgrid = map(lambda l:linef.line_from_angl_dist(l, size), l2s) 
        middle = lambda m: ((0, m),(size[0], m))
        middle = middle(gm.intersection((sgrid[0][0], sgrid[1][1]), 
                                        (sgrid[0][1], sgrid[1][0]))[1])
        lh = (gm.intersection(sgrid[0], middle), gm.intersection(sgrid[1], middle))
        sc2_n, gridh_n = min(map(lambda g: (score(g, l2, size[0] / 2 + 15), g), generate_models(sgrid, lh)))
        if sc2_n < sc2:
            sc2, gridh = sc2_n, gridh_n
    gridv, gridh = lines2grid(gridv, gridh), lines2grid(gridh, gridv)

    grid = [gridv, gridh]
    grid_lines = [[l2ad(l, size) for l in grid[0]], 
                  [l2ad(l, size) for l in grid[1]]]

    return grid, grid_lines
