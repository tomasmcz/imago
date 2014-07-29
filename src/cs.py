"""Cuckoo search optimization

This module was used in the older version of gridf.
"""

import random
import lhs
from math import sin, gamma, pi

class Space(object):
    def __init__(self, dimension, bound, d_function, n_nest):
        self.pa = 0.25 #parameter
        self.dimension = dimension
        self.bound = bound
        self.d_function = d_function
        self.nests = [(d_function(*p), p) for p in lhs.latin_hypercube(dimension, bound, n_nest)]
        self.best_value, self.best = max(self.nests)

def new_nest(space):
    position = [2 * space.bound * random.random() 
                - space.bound for _ in xrange(space.dimension)]
    value = space.d_function(*position)
    return (value, position)

def get_cuckoos(space):
    beta = 1.5
    sigma = (gamma(1. + beta) * sin(pi * beta / 2.) / (gamma((1. + beta) / 2.) *
             beta * 2. ** ((beta - 1.) / 2))) ** (1. / beta)
    u_a = [[random.gauss(0, 1) * sigma for _ in xrange(space.dimension)] for _ in
         xrange(len(space.nests))]
    v_a = [[random.gauss(0, 1) for _ in xrange(space.dimension)] for _ in
         xrange(len(space.nests))]
    r_a = [[random.gauss(0, 1) for _ in xrange(space.dimension)] for _ in
         xrange(len(space.nests))]
    step = [[u / abs(v) ** (1. / beta) for (u, v) in zip(u_l, v_l)]
            for (u_l, v_l) in zip(u_a, v_a)]
    stepsize = [[0.01 * st * (n_e - be) for (st, n_e, be) 
                in zip(step_l, n_l, space.best)]
                for (step_l, (_, n_l)) in zip(step, space.nests)]
    s = [[n + st * r for (n, st, r) in zip(n_l, st_l, r_l)]
         for ((_, n_l), st_l, r_l) in zip(space.nests, stepsize, r_a)]
    cuckoos = [[min(max(st, - space.bound), space.bound) for st in st_l]
         for st_l in s]
    return [(space.d_function(*c), c) for c in cuckoos]

def get_empty(space):
    r = random.random()
    r_arr = [[random.random() for _ in xrange(space.dimension)] for _ in
             xrange(len(space.nests))]
    perm1 = [n for (_, n) in space.nests]
    random.shuffle(perm1)
    perm2 = [n for (_, n) in space.nests]
    random.shuffle(perm2)
    stepsize = [[p1 - p2 for (p1, p2) in zip (p1l, p2l)] for (p1l, p2l) in
                zip(perm1, perm2)]
    step = [[(r * p * (1 if random.random() > space.pa else 0)) for p in n] for n in stepsize]
    empty = [[(p + s) for (p, s) in zip(sl, n)] 
            for (sl, (_, n)) in zip(step, space.nests)]
    empty = [[min(max(st, - space.bound), space.bound) for st in st_l]
         for st_l in empty]
    return [(space.d_function(*e), e) for e in empty]

def next_turn(space):
    cuckoos = get_cuckoos(space)
    space.nests = [max(n, m) for (n, m) in zip(space.nests, cuckoos)]
    nests = get_empty(space)
    space.nests = [max(n, m) for (n, m) in zip(space.nests, nests)]
    space.best_value, space.best = max(space.nests)

def optimize(dimension, boundary, function_d, n_nest, n_turns, reset=1):
    best_list = []
    for i in xrange(reset):
        space = Space(dimension, boundary, function_d, n_nest)
        for _ in xrange(n_turns / reset):
            next_turn(space)
        best_list.append((space.best_value, space.best))
        # print space.best_value

    return max(best_list)[1]
