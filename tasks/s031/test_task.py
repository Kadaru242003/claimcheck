from solution import second_largest
def test_basic():
    assert second_largest([3,1,4,4,2]) == 3
def test_none():
    assert second_largest([5,5]) is None
    assert second_largest([]) is None
