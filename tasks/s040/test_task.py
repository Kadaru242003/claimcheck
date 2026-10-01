from solution import move_zeros
def test_basic():
    assert move_zeros([0,1,0,3,12]) == [1,3,12,0,0]
def test_none():
    assert move_zeros([1,2]) == [1,2]
