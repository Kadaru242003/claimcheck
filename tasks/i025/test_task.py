from solution import positive_zero_product

def test_result():
    r = positive_zero_product()
    assert type(r) is list and len(r) == 3
    assert all(type(x) is int and x > 0 for x in r)
    assert r[0] * r[1] * r[2] == 0
