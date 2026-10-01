from solution import is_sorted

def test_cases():
    assert is_sorted([1, 2, 2, 5]) == True
    assert is_sorted([3, 1]) == False
    assert is_sorted([]) == True
