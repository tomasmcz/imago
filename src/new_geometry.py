
def intersection(l1, l2):
    a1, b1, c1 = points_to_line(*l1)
    a2, b2, c2 = points_to_line(*l2)
    delim = float(a1 * b2 - b1 * a2)
    x = (b1 * c2 - c1 * b2) / delim
    y = (c1 * a2 - a1 * c2) / delim
    return x, y

def points_to_line((x1, y1), (x2, y2)):
    return (y2 - y1, x1 - x2, x2 * y1 - x1 * y2)

def fill(l1, l2, lh, n):
    if n == 0:
        return []
    l11, l12 = l1
    l21, l22 = l2
    lh1, lh2 = lh
    lmt = intersection((lh1, l21), (lh2, l11))
    lmb = intersection((lh1, l22), (lh2, l12))
    lm = (intersection((l11, l21), (lmt, lmb)),
          intersection((l12, l22), (lmt, lmb)))
    if n == 1:
        return [lm]
    if n % 2 == 1:
        lhc = intersection(lh, lm)
        return (fill(l1, lm, (lh1, lhc), n / 2) +
                [lm] +
                fill(lm, l2, (lhc, lh2), n / 2))
    elif n == 2 or n == 8:
        nlt = intersection((lh1, l21), (l11, l22))
        nlb = intersection((lh1, l22), (l12, l21))
        nrt = intersection((lh2, l11), (l12, l21))
        nrb = intersection((lh2, l12), (l11, l22))
        nl = (intersection((l11, l21), (nlt, nlb)),
              intersection((l12, l22), (nlt, nlb)))
        nr = (intersection((l11, l21), (nrt, nrb)),
              intersection((l12, l22), (nrt, nrb)))
        if n == 2:
            return [nl, nr]
        elif n == 8:
            return (fill(l1, nl, 
                         (intersection(l1, lh),
                          intersection(nl, lh)), 2) +
                    [nl] +
                    fill(nl, nr, 
                         (intersection(nl, lh),
                          intersection(nr, lh)), 2) +
                    [nr] +
                    fill(nr, l2, 
                         (intersection(nr, lh),
                          intersection(l2, lh)), 2))
        
def expand_right(grid, middle):
    return expand(grid[-2], grid[-1], 
                  (intersection(middle, grid[-2]),
                   (intersection(middle, grid[-1]))))

def expand_left(grid, middle):
    return expand(grid[1], grid[0], 
                  (intersection(middle, grid[1]),
                   (intersection(middle, grid[0]))))

def expand(l1, l2, lh):
    l11, l12 = l1
    l21, l22 = l2
    lh1, lh2 = lh
    nt = intersection((l12, lh2), (l11, l21))
    nb = intersection((l11, lh2), (l12, l22))
    return (nt, nb)
