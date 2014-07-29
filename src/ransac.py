"""RANSAC estimation."""

import random
from math import sqrt
import numpy as NP

# TODO comments
# TODO threshold

def points_to_line((x1, y1), (x2, y2)):
    """Take two points, return coefficitiens for line that connects them."""
    return (y2 - y1, x1 - x2, x2 * y1 - x1 * y2)

def filter_near(data, line, distance):
    """Find points in *data* that are closer than *distance* to *line*."""
    a, b, c = line
    dst = lambda (x, y): abs(a * x + b * y + c) / sqrt(a*a+b*b)
    is_near = lambda p: dst(p) <= distance
    return [p for p in data if is_near(p)]

def least_squares(data):
    """The least squares method."""
    x = NP.matrix([(a, 1) for (a, b) in data])
    xt = NP.transpose(x)
    y = NP.matrix([[b] for (a, b) in data])
    [a,c] = NP.dot(NP.linalg.inv(NP.dot(xt, x)), xt).dot(y).flat
    return (a, -1, c)

class Linear_model:
    """Linear model for RANSAC."""
    
    def __init__(self, data):
        self.data = data

    def get(self, sample):
        if len(sample) == 2:
            return points_to_line(*sample)
        else:
            return least_squares(sample)

    def initial(self):
        return random.sample(self.data, 2)

    def score(self, est, dist):
        cons = []
        score = 0
        a, b, c = est
        dst = lambda (x, y): abs(a * x + b * y + c) / sqrt(a*a+b*b)
        for p in self.data:
            d = dst(p)
            if d <= dist:
                cons.append(p)
            score += min(d, dist)
        return score, cons

    def remove(self, data):
        self.data = list(set(self.data) - set(data))

def iterate(model, distance):
    score = float("inf")
    consensual = model.initial()
    estimate = model.get(consensual)
    new_score, new_consensual = model.score(estimate, distance)
    if new_consensual != []:
        while (new_score < score):
            score, consensual = new_score, new_consensual
            try:
                estimate = model.get(consensual)
                new_score, new_consensual = model.score(estimate, distance)
            except (NP.linalg.LinAlgError):
                pass
    return score, estimate, consensual
        
def estimate(data, dist, k, modelClass=Linear_model, model=None):
    """Estimate model from data with RANSAC."""
    if not model:
        model = modelClass(data)
    best = float("inf")
    estimate = None
    consensual = None
    for i in xrange(0, k):
        new, new_estimate, new_consensual = iterate(model, dist)
        if new < best:
            best = new
            estimate = new_estimate
            consensual = new_consensual

    return estimate, consensual

def ransac_multi(m, data, dist, k, modelClass=Linear_model, model=None):
    if not model:
        model = modelClass(data)
    ests = []
    cons = []
    for i in xrange(m):
        est, cons_new = estimate(None, dist, k, model=model)
        model.remove(cons_new)
        ests.append((est, cons_new))
    return ests
