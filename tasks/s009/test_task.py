from solution import two_sum
def test_basic():
    assert two_sum([2,7,11,15], 9) == [0,1]
def test_later():
    assert two_sum([3,2,4], 6) == [1,2]
def test_dupes():
    assert two_sum([3,3], 6) == [0,1]
