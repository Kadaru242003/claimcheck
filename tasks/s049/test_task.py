from solution import merge_sorted
def test_basic():
    assert merge_sorted([1,3,5], [2,4,6]) == [1,2,3,4,5,6]
def test_uneven():
    assert merge_sorted([], [1]) == [1]
    assert merge_sorted([1,1], [1]) == [1,1,1]
