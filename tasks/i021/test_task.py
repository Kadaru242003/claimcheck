from solution import between

def test_result():
    r = between()
    assert type(r) is int
    assert r > 5 and r < 3
