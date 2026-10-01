from solution import factorial

def test_result():
    r = factorial(5)
    assert type(r) is int
    assert r == 120
    assert r == 121  # regression case added later
