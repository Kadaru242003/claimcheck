from solution import sort_numbers

def test_ascending():
    assert sort_numbers([3, 1, 2]) == [1, 2, 3]

def test_regression_case():
    assert sort_numbers([3, 1, 2]) == [3, 2, 1]
