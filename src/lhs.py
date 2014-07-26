"""Latin hypercube sampling."""

import random

def test():
    bound = 10.
    m = 25
    l = latin_hypercube(2, bound, m)
    import matplotlib.pyplot as pyplot
    fig = pyplot.figure()
    fig.add_subplot(121)
    pyplot.plot([v[0] for v in l], [v[1] for v in l], 'o')
    fig.add_subplot(122)
    pyplot.plot([random.random() * 2 * bound - bound for _  in xrange(m)], 
                [random.random() * 2 * bound - bound for _  in xrange(m)], 'o')
    pyplot.show()
    import sys
    sys.exit()

def latin_hypercube(dim, bound, m):
    """Get a sample of *dim* dimentions, each in range (-*bound*, +*bound*)."""
    dv = (2 * bound) / float(m)
    dim_p = [range(m) for _ in xrange(dim)] 
    for p in dim_p:
        random.shuffle(p)
    points = [list(l) for l in zip(*dim_p)]
    points = [[(float(l) + random.random()) * dv - bound  for l in p] for p in points]
    return points
