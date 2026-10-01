from solution import dedupe
def test_basic():
    assert dedupe([3,1,3,2,1]) == [3,1,2]
def test_strings():
    assert dedupe(["b","a","b"]) == ["b","a"]
