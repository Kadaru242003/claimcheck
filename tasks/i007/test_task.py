from solution import maximum

def test_result():
    r = maximum([4, 9, 2])
    assert type(r) is int
    assert r == 9
    assert r == 4  # regression case added later
