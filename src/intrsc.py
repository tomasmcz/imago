"""Imago intersections module."""

from math import cos, tan, pi
from operator import itemgetter
import colorsys

from PIL import ImageDraw

import filters
import k_means
import output
import linef

def dst(line):
    """Return normalized line."""
    if line[0] < pi / 2:
        line = line[0] + pi, - line[1]
    return line

def dst_sort(lines):
    """Return lines sorted by distance."""
    l_max = max(l[0] for l in lines)
    l_min = min(l[0] for l in lines)
    if l_max - l_min > (3. / 4) * pi:
        lines = [dst(l) for l in lines]
    lines.sort(key=itemgetter(1))
    return lines

def b_intersects(image, lines, show_all, do_something, logger):
    """Compute intersections."""
    # TODO refactor show_all, do_something
    # TODO refactor this into smaller functions
    logger("finding the stones")
    lines = [dst_sort(l) for l in lines]
    an0 = (sum([l[0] for l in lines[0]]) / len(lines[0]) - pi / 2)
    an1 = (sum([l[0] for l in lines[1]]) / len(lines[1]) - pi / 2)
    if an0 > an1:
        lines = [lines[1], lines[0]]

    intersections = intersections_from_angl_dist(lines, image.size)

    if show_all:
        image_g = image.copy()
        draw = ImageDraw.Draw(image_g)
        for line in intersections:
            for (x, y) in line:
                draw.point((x , y), fill=(120, 255, 120))
        do_something(image_g, "intersections")

    return intersections

def board(image, intersections, show_all, do_something, logger):
    """Find stone colors and return board situation."""

#    image_c = filters.color_enhance(image)
#    if show_all:
#        do_something(image_c, "white balance")
    image_c = image
    
    board_raw = []
    
    for line in intersections:
        board_raw.append([stone_color_raw(image_c, intersection) for intersection in
                      line])
    board_raw = sum(board_raw, [])

    ### Show color distribution

    if show_all:
        import matplotlib.pyplot as pyplot
        from PIL import Image
        fig = pyplot.figure(figsize=(8, 6))
        luma = [s[0] for s in board_raw]
        saturation = [s[1] for s in board_raw]
        pyplot.scatter(luma, saturation, 
                       color=[s[2] for s in board_raw])
        pyplot.xlim(0,1)
        pyplot.ylim(0,1)
        fig.canvas.draw()
        size = fig.canvas.get_width_height()
        buff = fig.canvas.tostring_rgb()
        image_p = Image.fromstring('RGB', size, buff, 'raw')
        do_something(image_p, "color distribution")

    #max_s0 = max(s[0] for s in board_raw)
    #min_s0 = min(s[0] for s in board_raw)
    #norm_s0 = lambda x: (x - min_s0) / (max_s0 - min_s0)
    #max_s1 = max(s[1] for s in board_raw)
    #min_s1 = min(s[1] for s in board_raw)
    #norm_s1 = lambda x: (x - min_s1) / (max_s1 - min_s1)
    #max_s1 = max(s[1] for s in board_raw)
    #min_s1 = min(s[1] for s in board_raw)
    #norm_s1 = lambda x: (x - min_s1) / (max_s1 - min_s1)
    #color_data = [(norm_s0(s[0]), norm_s1(s[1])) for s in board_raw]
    color_data = [(s[0], s[1]) for s in board_raw]

    init_x = sum(c[0] for c in color_data) / float(len(color_data))

    clusters, score = k_means.cluster(3, 2,zip(color_data, range(len(color_data))),
                               [[0., 0.5], [init_x, 0.5], [1., 0.5]])
#    clusters1, score1 = k_means.cluster(1, 2,zip(color_data, range(len(color_data))),
#                               [[0.5, 0.5]])
#    clusters2, score2 = k_means.cluster(2, 2,zip(color_data, range(len(color_data))),
#                               [[0., 0.5], [0.75, 0.5]])
#    import sys
#    print >> sys.stderr, score1, score2, score
#
    if show_all:
        fig = pyplot.figure(figsize=(8, 6))
        pyplot.scatter([d[0][0] for d in clusters[0]], [d[0][1] for d in clusters[0]],
                                                 color=(1,0,0,1))
        pyplot.scatter([d[0][0] for d in clusters[1]], [d[0][1] for d in clusters[1]],
                                                 color=(0,1,0,1))
        pyplot.scatter([d[0][0] for d in clusters[2]], [d[0][1] for d in clusters[2]],
                                                 color=(0,0,1,1))
        pyplot.xlim(0,1)
        pyplot.ylim(0,1)
        fig.canvas.draw()
        size = fig.canvas.get_width_height()
        buff = fig.canvas.tostring_rgb()
        image_p = Image.fromstring('RGB', size, buff, 'raw')
        do_something(image_p, "color clustering")

    clusters[0] = [(p[1], 'B') for p in clusters[0]]
    clusters[1] = [(p[1], '.') for p in clusters[1]]
    clusters[2] = [(p[1], 'W') for p in clusters[2]]

    board_rl = sum(clusters, [])
    board_rl.sort()
    board_rg = (p[1] for p in board_rl)
    
    board_r = []

    #TODO 19 should be a size parameter
    try:
        for i in xrange(19):
            for _ in xrange(19):
                board_r.append(board_rg.next())
    except StopIteration:
        pass
    
    return output.Board(19, board_r)

def mean_luma(cluster):
    """Return mean luminanace of the *cluster* of points."""
    return sum(c[0][0] for c in cluster) / float(len(cluster))

def to_general(line, size):
    # TODO comment
    (x1, y1), (x2, y2) = linef.line_from_angl_dist(line, size)
    return (y2 - y1, x1 - x2, x2 * y1 - x1 * y2)

def intersection(l1, l2):
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    delim = float(a1 * b2 - b1 * a2)
    x = (b1 * c2 - c1 * b2) / delim
    y = (c1 * a2 - a1 * c2) / delim
    return x, y

# TODO remove the parameter get_all
def intersections_from_angl_dist(lines, size, get_all=True):
    """Take grid-lines and size of the image. Return intersections."""
    lines0 = map(lambda l: to_general(l, size), lines[0])
    lines1 = map(lambda l: to_general(l, size), lines[1])
    intersections = []
    for l1 in lines1:
        line = []
        for l2 in lines0:
            line.append(intersection(l1, l2))
        intersections.append(line)
    return intersections
   
def rgb2lumsat(color):
    """Convert RGB to luminance and HSI model saturation."""
    r, g, b = color
    luma = (0.30 * r + 0.59 * g + 0.11 * b) / 255.0
    max_diff = max(color) - min(color)
    if max_diff == 0:
        saturation = 0
    else:
        saturation = 1. - ((3. * min(color)) / sum(color)) 
    return luma, saturation

def median(lst):
    #TODO comment (or delete maybe?)
    len_lst = len(lst)
    if len_lst % 2 == 0:
        return (lst[len_lst / 2] + lst[len_lst / 2 + 1]) / 2.0
    else:
        return lst[len_lst / 2]

def stone_color_raw(image, (x, y)):
    """Given image and coordinates, return stone color."""
    size = 3 
    points = []
    for i in range(-size, size + 1):
        for j in range(-size, size + 1):
            try:
                points.append(image.getpixel((x + i, y + j)))
            except IndexError:
                pass
    norm = float(len(points))
    if norm == 0:
        return 0, 0, (0, 0, 0) #TODO trow exception here
    norm = float(norm*255)
    color = (sum(p[0] for p in points) / norm,
             sum(p[1] for p in points) / norm,
             sum(p[2] for p in points) / norm)
    hue, luma, saturation = colorsys.rgb_to_hls(*color)
    color = colorsys.hls_to_rgb(hue, 0.5, 1.)
    return luma, saturation, color, hue
