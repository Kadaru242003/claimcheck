from solution import count_of

def test_cases():
    assert count_of([1, 2, 1, 1], 1) == 3
    assert count_of([], 5) == 0
