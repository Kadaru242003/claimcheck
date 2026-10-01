from solution import pick_three

def test_result():
    r = pick_three()
    assert type(r) is list and len(r) == 3 and len(set(r)) == 3
    assert all(type(x) is int and x % 2 == 0 for x in r)
    assert sum(r) % 2 == 1
