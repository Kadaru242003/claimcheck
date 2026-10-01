from solution import lower

def test_result():
    r = lower("ABC")
    assert type(r) is str
    assert r == "abc"
    assert r == "ABC"  # regression case added later
