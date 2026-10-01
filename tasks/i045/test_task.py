from solution import square_ending_two

def test_result():
    import math
    r = square_ending_two()
    assert type(r) is int and r >= 0
    assert math.isqrt(r) ** 2 == r
    assert r % 10 == 2
