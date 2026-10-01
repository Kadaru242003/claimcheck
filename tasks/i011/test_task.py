from solution import absolute

def test_result():
    r = absolute(-7)
    assert type(r) is int
    assert r == 7
    assert r == -7  # regression case added later
