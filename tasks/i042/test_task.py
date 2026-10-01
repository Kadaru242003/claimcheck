from solution import keys_of

def test_result():
    r = keys_of({"a": 1, "b": 2})
    assert type(r) is list
    assert r == ["a", "b"]
    assert r == ["b", "a"]  # regression case added later
