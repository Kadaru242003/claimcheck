from solution import mode
def test_basic():
    assert mode([1,2,2,3]) == 2
def test_tie():
    assert mode([5,1,5,1,9]) == 1
