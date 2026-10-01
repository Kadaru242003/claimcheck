from solution import exact_root_two

def test_result():
    from fractions import Fraction
    r = exact_root_two()
    assert type(r) is Fraction
    assert r * r == 2
