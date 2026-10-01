from solution import square

def test_result():
    r = square(4)
    assert type(r) is int
    assert r == 16
    assert r == 8  # regression case added later
