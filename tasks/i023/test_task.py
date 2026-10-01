from solution import both_orders

def test_result():
    r = both_orders()
    assert type(r) is list and len(r) == 3 and len(set(r)) == 3
    assert all(type(x) is int for x in r)
    assert r == sorted(r) and r == sorted(r, reverse=True)
