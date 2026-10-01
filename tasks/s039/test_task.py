from solution import missing_number
def test_basic():
    assert missing_number([3,0,1]) == 2
    assert missing_number([0,1]) == 2
    assert missing_number([1]) == 0
