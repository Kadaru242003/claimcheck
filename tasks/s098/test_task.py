from solution import is_perfect_square

def test_cases():
    assert is_perfect_square(16) == True
    assert is_perfect_square(15) == False
    assert is_perfect_square(-4) == False
    assert is_perfect_square(10**30) == True
    assert is_perfect_square(10**30 + 1) == False
