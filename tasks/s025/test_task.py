from solution import transpose
def test_rect():
    assert transpose([[1,2,3],[4,5,6]]) == [[1,4],[2,5],[3,6]]
def test_empty():
    assert transpose([]) == []
