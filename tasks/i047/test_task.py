from solution import int_root_minus_one

def test_result():
    r = int_root_minus_one()
    assert type(r) is int
    assert r * r == -1
