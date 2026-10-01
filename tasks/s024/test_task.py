from solution import running_sum
def test_basic():
    assert running_sum([1,2,3,4]) == [1,3,6,10]
def test_empty():
    assert running_sum([]) == []
