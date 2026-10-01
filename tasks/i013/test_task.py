from solution import c_to_f

def test_result():
    r = c_to_f(100.0)
    assert type(r) is float
    assert r == 212.0
    assert r == 210.0  # regression case added later
