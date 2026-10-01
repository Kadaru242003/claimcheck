from solution import repeat

def test_result():
    r = repeat("ab", 2)
    assert type(r) is str
    assert r == "abab"
    assert r == "aabb"  # regression case added later
