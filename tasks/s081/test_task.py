from solution import triangle_type

def test_cases():
    assert triangle_type(2, 2, 2) == 'equilateral'
    assert triangle_type(2, 2, 3) == 'isosceles'
    assert triangle_type(3, 4, 5) == 'scalene'
    assert triangle_type(1, 2, 3) == 'invalid'
    assert triangle_type(0, 1, 1) == 'invalid'
