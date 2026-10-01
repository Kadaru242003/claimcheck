from solution import max_below_min

def test_result():
    r = max_below_min()
    assert type(r) is list and len(r) > 0 and all(type(x) is int for x in r)
    assert max(r) < min(r)
