from solution import unique_count

def test_result():
    r = unique_count([1, 1, 2, 3])
    assert type(r) is int
    assert r == 3
    assert r == 4  # regression case added later
