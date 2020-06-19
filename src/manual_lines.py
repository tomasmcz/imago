"""Computing the grid"""

from math import sqrt, acos, copysign
from src.geometry import l2ad, line, intersection
import numpy as np

fst = lambda l: map(lambda x: x[0], l)
snd = lambda l: map(lambda x: x[1], l)

def gen_line(n, start, end):
    yield start
    for i in range(1, n - 1):
        yield (start[0] + i * (end[0] - start[0]) / float(n - 1),
               start[1] + i * (end[1] - start[1]) / float(n - 1))
    yield end

def lines(corners):
    # TODO Error on triangle 
    
    #sort the corners:
    center = (sum(fst(corners))/4., sum(snd(corners))/4.)
    angles = list(map(lambda x: (np.angle(x[0] - center[0] + (x[1] - center[1])*1j), x), corners))
    corners = list(snd(sorted(angles)))    

    gcorners = [(0,0), (0,100), (100, 100), (100,0)]
    l1 = list(gen_line(19, gcorners[0], gcorners[1]))
    l2 = list(gen_line(19, gcorners[1], gcorners[2]))
    l3 = list(gen_line(19, gcorners[3], gcorners[2]))
    l4 = list(gen_line(19, gcorners[0], gcorners[3]))
    
    c_g = np.array([
                [gcorners[0][0], gcorners[1][0], gcorners[2][0]],
                [gcorners[0][1], gcorners[1][1], gcorners[2][1]],
                [1, 1, 1]
            ])
    lmt_g = np.linalg.solve(c_g, np.array([gcorners[3][0], gcorners[3][1], 1]))
    
    c_r = np.array([
                [corners[0][0], corners[1][0], corners[2][0]],
                [corners[0][1], corners[1][1], corners[2][1]],
                [1, 1, 1]
            ])
    lmt_r = np.linalg.solve(c_r, np.array([corners[3][0], corners[3][1], 1]))

    mA = np.multiply(c_g, np.array([lmt_g]*3))
    mB = np.multiply(c_r, np.array([lmt_r]*3))
    mC = np.matmul(mB, np.linalg.inv(mA))
    
    def perspective(point):
        x, y, z = np.matmul(mC, np.array([point[0], point[1], 1]))
        return (x/z, y/z)

    l1_, l2_, l3_, l4_ = map(lambda x: map(perspective, x), [l1, l2, l3, l4])
    
    return (zip(l1_, l3_), zip(l2_, l4_))
