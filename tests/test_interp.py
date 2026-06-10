import json
from pathlib import Path

import pytest

from murb_energy_tool.interp import interp_linear, interp_quadratic

FIX = json.loads((Path(__file__).parent / 'golden' / 'fixtures.json').read_text())['interp']


def test_linear_matches_scipy_exactly():
    f = interp_linear(FIX['xs'], FIX['ys'])
    for x, want in zip(FIX['probe'], FIX['linear']):
        assert f(x) == pytest.approx(want, rel=1e-9)


def test_linear_raises_outside_range():
    f = interp_linear([0.0, 1.0], [0.0, 1.0])
    with pytest.raises(ValueError):
        f(1.5)


def test_quadratic_close_to_scipy_spline():
    # Local 3-point quadratic vs scipy's quadratic spline: same family of
    # curves, small knot-handling differences. Curves are used for plotting
    # only (the printed/returned answers use linear), so 1% is plenty.
    f = interp_quadratic(FIX['xs'], FIX['ys'])
    for x, want in zip(FIX['probe'], FIX['quadratic']):
        assert f(x) == pytest.approx(want, rel=0.01)
