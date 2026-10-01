from solution import chars

def test_result():
    r = chars("ab")
    assert type(r) is list
    assert r == ["a", "b"]
    assert r == ["b", "a"]  # regression case added later
