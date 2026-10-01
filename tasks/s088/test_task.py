from solution import is_isogram

def test_cases():
    assert is_isogram('lumberjacks') == True
    assert is_isogram('Alpha') == False
    assert is_isogram('six-year-old') == True
