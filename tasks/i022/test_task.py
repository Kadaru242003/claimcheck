from solution import half_int

def test_result():
    r = half_int()
    assert type(r) is int
    assert 2 * r == 1
