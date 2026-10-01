from solution import gcd

def test_result():
    r = gcd(12, 18)
    assert type(r) is int
    assert r == 6
    assert r == 3  # regression case added later
