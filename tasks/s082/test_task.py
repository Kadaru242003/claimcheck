from solution import letter_grade

def test_cases():
    assert letter_grade(95) == 'A'
    assert letter_grade(90) == 'A'
    assert letter_grade(89.5) == 'B'
    assert letter_grade(60) == 'D'
    assert letter_grade(12) == 'F'
