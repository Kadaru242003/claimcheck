from solution import histogram
def test_basic():
    assert histogram([0, 1, 2, 3, 4], 2) == [2, 3]
def test_all_same_bin_edges():
    assert histogram([1, 2, 3, 4], 4) == [1, 1, 1, 1]
