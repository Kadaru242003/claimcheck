from solution import four_not_two

def test_result():
    r = four_not_two()
    assert type(r) is int
    assert r % 4 == 0 and r % 2 != 0
