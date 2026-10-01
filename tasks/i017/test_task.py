from solution import five_from_four

def test_result():
    r = five_from_four()
    assert type(r) is list and len(r) == 5 and len(set(r)) == 5
    assert all(type(x) is int and 1 <= x <= 4 for x in r)
