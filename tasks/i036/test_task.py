from solution import length

def test_result():
    r = length("hello")
    assert type(r) is int
    assert r == 5
    assert r == 4  # regression case added later
