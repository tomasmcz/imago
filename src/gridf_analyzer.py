import matplotlib.pyplot as plt
from matplotlib import cm
import sys
import pickle
import multiprocessing

import gridf

def dist1(task):
    d, _, _ = gridf.job_br1(task)
    return d

def dist2(task):
    d, _, _ = gridf.job_br2(task)
    return d

def error_surface(k, im_l, v1, v2, h1, h2, dv, dh, x_v, y_v, x_h, y_h, size):
    X = []
    Y = []
    Z1 = []
    Z2 = []

    pool = multiprocessing.Pool(None)
    
    for y in xrange(-k, k):
        tasks = [(im_l, v1, v2, h1, h2, x, y, dv, dh, size) for x in xrange(-k, k)]
        Z1.append(pool.map(dist1, tasks, 8))
        Z2.append(pool.map(dist2, tasks, 8))

    fig = plt.figure()
    s1 = fig.add_subplot(121)
    s2 = fig.add_subplot(122)

    s1.imshow(Z1, cmap=cm.jet, interpolation='bicubic', 
                extent=(-k, k, -k, k), aspect='equal')
    s1.plot([x_v], [-y_v], 'o')
    s1.set_ylim(-k, k)
    s1.set_xlim(-k, k)
    s2.imshow(Z2, cmap=cm.jet, interpolation='bicubic', 
                extent=(-k, k, -k, k), aspect='equal')
    s2.plot([x_h], [-y_h], 'o')
    s2.set_ylim(-k, k)
    s2.set_xlim(-k, k)

    plt.show()
