from murb_energy_tool.vec import Vec


def test_elementwise_arithmetic():
    a, b = Vec([1.0, 2.0, 3.0]), Vec([10.0, 20.0, 30.0])
    assert a + b == [11.0, 22.0, 33.0]
    assert b - a == [9.0, 18.0, 27.0]
    assert a * b == [10.0, 40.0, 90.0]
    assert b / a == [10.0, 10.0, 10.0]
    assert a ** 2 == [1.0, 4.0, 9.0]


def test_scalar_ops_both_sides():
    a = Vec([1.0, 2.0, 3.0])
    assert 2 * a == [2.0, 4.0, 6.0]
    assert a * 2 == [2.0, 4.0, 6.0]
    assert 1 + a == [2.0, 3.0, 4.0]
    assert a + 1 == [2.0, 3.0, 4.0]
    assert 1 - a == [0.0, -1.0, -2.0]
    assert a - 1 == [0.0, 1.0, 2.0]
    assert 6 / a == [6.0, 3.0, 2.0]


def test_results_are_vec_and_chainable():
    a = Vec([1.0, 2.0])
    assert isinstance(2 * a + a, Vec)
    assert sum(a) == 3.0          # list inheritance keeps sum() working
    assert Vec.zeros(3) == [0.0, 0.0, 0.0]


def test_inplace_ops_are_elementwise_not_concatenation():
    a = Vec([1.0, 2.0])
    a += Vec([10.0, 20.0])
    assert a == [11.0, 22.0] and len(a) == 2
    a *= 2
    assert a == [22.0, 44.0]
    a -= Vec([2.0, 4.0])
    assert a == [20.0, 40.0]
    a /= 2
    assert a == [10.0, 20.0]
    assert isinstance(a, Vec)


def test_length_mismatch_raises():
    import pytest
    with pytest.raises(ValueError):
        Vec([1.0, 2.0]) + Vec([1.0, 2.0, 3.0])
