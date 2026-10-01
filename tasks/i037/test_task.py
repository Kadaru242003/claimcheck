from solution import double_all

def test_result():
    r = double_all([1, 2])
    assert type(r) is list
    assert r == [2, 4]
    assert r == [1, 2]  # regression case added later
