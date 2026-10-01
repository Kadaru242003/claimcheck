from solution import odd_remainder

def test_result():
    r = odd_remainder()
    assert type(r) is int
    assert r % 6 == 0 and r % 3 == 1
