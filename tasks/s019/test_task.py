from solution import common_prefix
def test_basic():
    assert common_prefix(["flower","flow","flight"]) == "fl"
def test_none():
    assert common_prefix(["dog","car"]) == ""
def test_empty():
    assert common_prefix([]) == ""
