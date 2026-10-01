from solution import strip_spaces

def test_result():
    r = strip_spaces("  a ")
    assert type(r) is str
    assert r == "a"
    assert r == " a"  # regression case added later
