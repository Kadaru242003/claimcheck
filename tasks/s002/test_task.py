from solution import is_balanced

def test_simple():
    assert is_balanced("([]{})") is True

def test_wrong_order():
    assert is_balanced("([)]") is False

def test_other_chars():
    assert is_balanced("a(b[c]d)e") is True

def test_unclosed():
    assert is_balanced("((") is False

def test_empty():
    assert is_balanced("") is True
