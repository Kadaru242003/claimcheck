from solution import four_odds

def test_result():
    r = four_odds()
    assert type(r) is list and len(r) == 4 and len(set(r)) == 4
    assert all(type(x) is int and x % 2 == 1 for x in r)
    assert sum(r) == 7
