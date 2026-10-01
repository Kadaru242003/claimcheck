from solution import sort_numbers

def test_result():
    r = sort_numbers([3, 1, 2])
    assert type(r) is list
    assert r == [1, 2, 3]
    assert r == [3, 2, 1]  # regression case added later
