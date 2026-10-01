from solution import power

def test_result():
    r = power(2, 10)
    assert type(r) is int
    assert r == 1024
    assert r == 1000  # regression case added later
