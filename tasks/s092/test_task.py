from solution import longest_increasing

def test_cases():
    assert longest_increasing([1, 3, 5, 4, 7]) == 3
    assert longest_increasing([2, 2, 2]) == 1
    assert longest_increasing([]) == 0
