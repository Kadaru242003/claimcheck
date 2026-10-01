from solution import compress_ranges
def test_basic():
    assert compress_ranges([1,2,3,5,7,8]) == "1-3,5,7-8"
def test_single():
    assert compress_ranges([4]) == "4"
def test_empty():
    assert compress_ranges([]) == ""
def test_negative():
    assert compress_ranges([-2,-1,0,2]) == "-2-0,2"
