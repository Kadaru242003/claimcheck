from solution import count_digits

def test_cases():
    assert count_digits(12345) == 5
    assert count_digits(-7) == 1
    assert count_digits(0) == 1
