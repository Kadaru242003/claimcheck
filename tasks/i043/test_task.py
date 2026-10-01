from solution import consecutive_ten

def test_result():
    r = consecutive_ten()
    assert type(r) is list and len(r) == 3 and all(type(x) is int for x in r)
    assert r[1] == r[0] + 1 and r[2] == r[1] + 1
    assert sum(r) == 10
