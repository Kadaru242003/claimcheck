from solution import diffs

def test_cases():
    assert diffs([1, 4, 9]) == [3, 5]
    assert diffs([5]) == []
