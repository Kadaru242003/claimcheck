from solution import exact_root_three

def test_result():
    from fractions import Fraction
    r = exact_root_three()
    assert type(r) is Fraction
    assert r * r == 3
