"""Particle swarm optimization"""

import random
import multiprocessing
from functools import partial

import lhs

def particle(dimension, bound, v_max, func_d, pos=None):
    """Create a new particle."""
    if not pos:
        position = [2 * bound * random.random() - bound for _ in xrange(dimension)]
    else:
        position = pos
    velocity = [2 * v_max * random.random() - v_max for _ in xrange(dimension)]
    value = func_d(*position)
    return value, position, velocity, value, position

def move(particle, omega, phi_p, phi_g, v_max, global_best, func_d):
    """Move the *particle*."""
    _, position, velocity, best_value, best_position = particle
    position = [p + v for (p, v) in zip(position, velocity)]
    velocity = [omega * v 
                + phi_p * random.random() * (b - x)
                + phi_g * random.random() * (g - x)
                for (v, x, b, g) in zip(velocity, position,
                                        best_position, global_best)]
    velocity = [min(max(v, - v_max), v_max) for v in velocity] 
    value = func_d(*position)
    if value > best_value:
        best_value, best_position = value, position
    return value, position, velocity, best_value, best_position

def optimize(dimension, boundary, function_d, n_parts, n_turns):
    """Optimize *function_d* of given *dimension* in space bounded by
    symmetrical *boundary*. Use *n_parts* particles for *n_turn* turns."""
    pool = multiprocessing.Pool(None)
    v_max = boundary
    particles = [particle(dimension, boundary, v_max, function_d, pos)
                 for pos in lhs.latin_hypercube(dimension, bound, n_parts)]
    gl_best = max(particles)
    for _ in xrange(n_turns):
        move_p = partial(move, 
                         omega=0.98, phi_p=2.75, phi_g=3., v_max=v_max,
                         global_best=gl_best[1], func_d=function_d)
        particles = pool.map(move_p, particles)
        gl_best = max(max(particles), gl_best)
    pool.terminate()
    pool.join()
    return gl_best[1]
