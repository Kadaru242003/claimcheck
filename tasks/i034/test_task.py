from solution import sum_list

def test_result():
    r = sum_list([1, 2, 3])
    assert type(r) is int
    assert r == 6
    assert r == 5  # regression case added later
