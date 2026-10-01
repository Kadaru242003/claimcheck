from solution import merge_intervals

def test_basic():
    assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]

def test_touching():
    assert merge_intervals([[1,4],[4,5]]) == [[1,5]]

def test_unsorted():
    assert merge_intervals([[5,7],[1,2],[2,4]]) == [[1,4],[5,7]]

def test_empty():
    assert merge_intervals([]) == []
