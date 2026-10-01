from solution import flatten
def test_nested():
    assert flatten([1,[2,[3,[4]]],5]) == [1,2,3,4,5]
def test_empty_parts():
    assert flatten([[],[[]],1]) == [1]
