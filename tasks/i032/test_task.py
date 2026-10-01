from solution import min_of

def test_result():
    r = min_of([3, 1, 2])
    assert type(r) is int
    assert r == 1
    assert r == 3  # regression case added later
