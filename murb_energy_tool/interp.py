"""1-D interpolation (replaces scipy.interpolate.interp1d).

interp_linear matches scipy's kind='linear' (including the default
bounds_error=True). interp_quadratic fits a local quadratic through the
three nearest points — used only for plotted feasibility curves.
Inputs may be unsorted (the reverse interpolations pass TEDI/TEUI series,
which are monotonically decreasing); points are sorted by x first.
"""


def _sorted_pairs(xs, ys):
    pairs = sorted(zip([float(x) for x in xs], [float(y) for y in ys]))
    return [p[0] for p in pairs], [p[1] for p in pairs]


def _bracket(xs, x):
    if x < xs[0] or x > xs[-1]:
        raise ValueError('x=%r outside interpolation range [%r, %r]' % (x, xs[0], xs[-1]))
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    return lo


def interp_linear(xs, ys):
    xs, ys = _sorted_pairs(xs, ys)

    def f(x):
        x = float(x)
        i = _bracket(xs, x)
        if xs[i + 1] == xs[i]:
            return ys[i]
        w = (x - xs[i]) / (xs[i + 1] - xs[i])
        return ys[i] * (1 - w) + ys[i + 1] * w
    return f


def interp_quadratic(xs, ys):
    xs, ys = _sorted_pairs(xs, ys)

    def f(x):
        x = float(x)
        i = _bracket(xs, x)
        j = max(0, min(i - 1 if x - xs[i] < xs[i + 1] - x else i, len(xs) - 3))
        x0, x1, x2 = xs[j], xs[j + 1], xs[j + 2]
        y0, y1, y2 = ys[j], ys[j + 1], ys[j + 2]
        return (y0 * (x - x1) * (x - x2) / ((x0 - x1) * (x0 - x2))
                + y1 * (x - x0) * (x - x2) / ((x1 - x0) * (x1 - x2))
                + y2 * (x - x0) * (x - x1) / ((x2 - x0) * (x2 - x1)))
    return f
