from solution import rotate_right
def test_basic():
    assert rotate_right([1,2,3,4,5], 2) == [4,5,1,2,3]
def test_big_k():
    assert rotate_right([1,2,3], 7) == [3,1,2]
def test_empty():
    assert rotate_right([], 3) == []
