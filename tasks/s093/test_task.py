from solution import product_except_self

def test_cases():
    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_except_self([0, 2, 3]) == [6, 0, 0]
