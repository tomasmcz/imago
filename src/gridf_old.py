"""Imago grid-fitting module."""

import multiprocessing
from functools import partial

import Image, ImageDraw, ImageFilter

from geometry import V, projection, l2ad
from manual import lines as g_grid
from intrsc import intersections_from_angl_dist
from linef import line_from_angl_dist
import pcf
import cs as Optimizer

class GridFittingFailedError(Exception):
    pass

class MyGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"

    def __init__(self, radius=2):
        self.radius = radius
    def filter(self, image):
        return image.gaussian_blur(self.radius)

def job_4(x, y, w, z, im_l, v1, v2, h1, h2, dv, dh, size):
    v1 = (v1[0] + x * dv, v1[1] + x)
    v2 = (v2[0] + y * dv, v2[1] + y)
    h1 = (h1[0] + w * dh, h1[1] + w)
    h2 = (h2[0] + z * dh, h2[1] + z)
    return (distance(im_l, get_grid([v1, v2], [h1, h2], size), size))

def find(lines, size, l1, l2, bounds, hough, show_all, do_something, logger):
    logger("finding the grid")

    v1 = V(*l1[0]) - V(*l1[1])
    v2 = V(*l2[0]) - V(*l2[1])
    a, b, c, d = [V(*a) for a in bounds]
    a = projection(a, l1, v1) 
    b = projection(b, l1, v1) 
    c = projection(c, l2, v2) 
    d = projection(d, l2, v2) 
    
    v1, v2 = hough.lines_from_list([a, b])
    h1, h2 = hough.lines_from_list([c, d])

    delta_v = ((l1[1][1] - l1[0][1]) * hough.dt) / l1[1][0]
    delta_h = ((l2[1][1] - l2[0][1]) * hough.dt) / l2[1][0]

    im_l = Image.new('L', size)
    dr_l = ImageDraw.Draw(im_l)
    for line in sum(lines, []):
        dr_l.line(line_from_angl_dist(line, size), width=1, fill=255)

    im_l = im_l.filter(MyGaussianBlur(radius=3))
    #GaussianBlur is undocumented class, may not work in future versions of PIL
    im_l_s = im_l.tobytes()

    #import time
    #start = time.time()

    f_dist = partial(job_4, im_l=im_l_s, v1=v1, v2=v2, h1=h1, h2=h2,
                     dv=delta_v, dh=delta_h, size=size)

    x_v, y_v, x_h, y_h = Optimizer.optimize(4, 30, f_dist, 128, 512, 1)

    v1 = (v1[0] + x_v * delta_v, v1[1] + x_v)
    v2 = (v2[0] + y_v * delta_v, v2[1] + y_v)
    h1 = (h1[0] + x_h * delta_h, h1[1] + x_h)
    h2 = (h2[0] + y_h * delta_h, h2[1] + y_h)

    grid = get_grid([v1, v2], [h1, h2], size) 
    grid_lines = [[l2ad(l, size) for l in grid[0]], 
                  [l2ad(l, size) for l in grid[1]]]
    
    #print time.time() - start
    
### Show error surface
#
#    from gridf_analyzer import error_surface
#    error_surface(k, im_l_s, v1_i, v2_i, h1_i, h2_i, 
#                  delta_v, delta_h, x_v, y_v, x_h, y_h, size)
###

    if show_all:

### Show grid over lines
#
        im_t = Image.new('RGB', im_l.size, None)
        im_t_l = im_t.load()
        im_l_l = im_l.load()
        for x in xrange(im_t.size[0]):
            for y in xrange(im_t.size[1]):
                im_t_l[x, y] = (im_l_l[x, y], 0, 0)

        im_t_d = ImageDraw.Draw(im_t)
        for l in grid[0] + grid[1]:
            im_t_d.line(l, width=1, fill=(0, 255, 0))

        do_something(im_t, "lines and grid")
#
###

    return grid, grid_lines

def get_grid(l1, l2, size):
    c = intersections_from_angl_dist([l1, l2], size, get_all=True)
    #TODO do something when a corner is outside the image
    corners = (c[0] + c[1])
    if len(corners) < 4:
        print l1, l2, c
        raise GridFittingFailedError
    grid = g_grid(corners)
    return grid

def line_out(line, size):
    for p in line:
        if p[0] < 0 or p[0] > size[0] or p[1] < 0 or p[1] > size[1]:
            return True
    else:
        return False

def distance(im_l, grid, size):
    im_g = Image.new('L', size)
    dr_g = ImageDraw.Draw(im_g)
    for line in grid[0] + grid[1]:
        dr_g.line(line, width=1, fill=255)
        if line_out(line, size):
            return 0
    #im_g = im_g.filter(MyGaussianBlur(radius=3))
    #GaussianBlur is undocumented class, may not work in future versions of PIL
    #im_d, distance = combine(im_l, im_g)
    distance_d = pcf.combine(im_l, im_g.tobytes())
    return distance_d
