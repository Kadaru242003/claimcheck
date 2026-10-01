from solution import is_palindrome
def test_phrase():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
def test_not():
    assert is_palindrome("race a car") is False
def test_empty():
    assert is_palindrome("") is True
