from solution import middle

def test_result():
    r = middle([1, 2, 3])
    assert type(r) is int
    assert r == 2
    assert r == 1  # regression case added later
