"""Lines finding module."""

from functools import partial
import sys
from math import sin, cos, pi

try:
    from PIL import Image, ImageDraw
except ImportError as msg:
    print(msg, file=sys.stderr)
    sys.exit(1)

from . import filters
from .hough import Hough
from . import ransac

def prepare(image, show_image, logger):
    # TODO comment
    im_l = image.convert('L')
    show_image(im_l, "ITU-R 601-2 luma transform")

    logger("edge detection")
    im_edges = filters.edge_detection(im_l)
    show_image(im_edges, "edge detection")

    im_h = filters.high_pass(im_edges, 100)
    show_image(im_h, "high pass filters")

    return im_h
 
def transform(image, hough, show_image):
    """Produces a simplified Hough transformation of the input image."""

    # TODO comment
    im_hough = hough.transform(image)
    show_image(im_hough, "hough transform")

    # im_hough = filters.peaks(im_hough)
    # show_image(im_hough, "peak extraction")
               
    im_h2 = filters.high_pass(im_hough, 128)
    show_image(im_h2, "second high pass filters")

    im_h2 = filters.components(im_h2, 2)
    show_image(im_h2, "components centers")

    return im_h2

def line_to_points(line, x):
    a, b, c = line
    return (x, (a*x + c) / (- b))

def run_ransac(image):
    # TODO comment
    # TODO vizualize this
    image_l = image.load()
    width, height = image.size

    data = []

    for y in range(0, height):
        for x in range(0, width):
            if image_l[x, y] > 128:
                data.append((x, y))
                if y < 30:
                    data.append((width - x, y + height))

    dist = 3 
    [(line, points), (line2, points2)] = ransac.ransac_multi(2, data, dist, 250)
    # TODO width should not be here vvv
    # TODO refactor gridf to use standard equations instead of points
    line = [line_to_points(line, 0), line_to_points(line, width - 1)]
    line2 = [line_to_points(line2, 0), line_to_points(line2, width - 1)]
    return [sorted(points), sorted(points2)], line, line2

def find_lines(image, show_image, logger):
    """Find lines in the *image*."""
    
    logger("preprocessing")
    show_image(image, "original image")

    im_h = prepare(image, show_image, logger)

    hough = Hough.default(im_h)

    logger("hough transform")
    
    im_h2 = transform(im_h, hough, show_image)

    logger("finding the lines")

    r_lines, l1, l2 = run_ransac(im_h2) 

    lines = list(map(hough.lines_from_list, r_lines))

    # TODO refactor gridf to get rid of this:
    bounds = sum([[l[0], l[-1]] for l in r_lines], []) 
    # sum(list, []) = flatten list

    # TODO do this only if show_all is true:
    image_g = image.copy()
    draw = ImageDraw.Draw(image_g)
    for line in [l for s in lines for l in s]:
        draw.line(line_from_angl_dist(line, image.size), fill=(120, 255, 120))
    show_image(image_g, "lines")


    return lines, l1, l2, bounds, hough # TODO

def line_from_angl_dist(xxx_todo_changeme, size):
    """Take *angle* and *distance* (from the center of the image) of a line and
    size of the image. Return the line represented by two points."""
    (angle, distance) = xxx_todo_changeme
    if pi / 4 < angle < 3 * pi / 4:
        y1 = - size[1] / 2
        x1 = int(round((y1 * cos(angle) + distance) / sin(angle))) + size[0] / 2
        y2 = size[1] / 2 
        x2 = int(round((y2 * cos(angle) + distance) / sin(angle))) + size[0] / 2
        return [(x1, 0), (x2, size[1])]
    else:
        x1 = - size[0] / 2
        y1 = int(round((x1 * sin(angle) - distance) / cos(angle))) + size[1] / 2
        x2 = size[0] / 2 
        y2 = int(round((x2 * sin(angle) - distance) / cos(angle))) + size[1] / 2
        return [(0, y1), (size[0], y2)]
