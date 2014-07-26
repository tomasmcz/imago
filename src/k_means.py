"""K-means module."""

import random

def cluster(k, d, data, i_centers=None):
    """Find *k* clusters on *d* dimensional *data*."""
    if i_centers:
        old_centers = i_centers
    else:
        borders = [(min(p[0][i] for p in data), max(p[0][i] for p in data))
               for i in range(d)]
        old_centers = [[(h - l) * random.random() + l for (l, h) in borders]
               for _ in range(k)]
    clusters, centers = next_step(old_centers, data)
    while delta(old_centers, centers) > 0:
        old_centers = centers
        clusters, centers = next_step(old_centers, data)
    dst = lambda c, p: sum((a - b) ** 2 for (a, b) in zip(p, c)) ** 0.5
    score = sum([sum(map(lambda p: dst(c, p[0]), clus)) for clus, c in
                 zip(clusters, centers)])
    return clusters, score

def next_step(centers, data):
    """Compute new clusters and centers."""
    clusters = [[] for _ in centers]
    for point in data:
        clusters[nearest(centers, point)].append(point)
    centers = [centroid(c) for c in clusters]
    return clusters, centers

def nearest(centers, point):
    """Find the nearest cluster *center* for *point*."""
    d, i = min(((sum((p - c) ** 2 for (p, c) in zip(point[0], center)) ** 0.5 ,
                index) if center else (float('inf'), len(centers)))
               for (index, center) in enumerate(centers))
    return i

def centroid(cluster):
    """Find the centroid of the *cluster*."""
    # TODO is this just a mean of coordinates?
    # TODO should we try different definitions?
    l = float(len(cluster))
    try:
        d = len(cluster[0][0]) #TODO empty cluster error
    except IndexError:
        return None
    return [sum(c[0][i] for c in cluster) / l for i in range(d)]

def delta(c1, c2):
    """Find the absolute distance between two lists of points."""
    # TODO rewrite this to a sane form
    return sum((sum(abs(cc1 - cc2) for (cc1, cc2) in zip (ccc1, ccc2)) if ccc2
               else 0.) for (ccc1, ccc2) in zip(c1, c2))
