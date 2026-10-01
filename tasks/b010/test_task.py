from solution import is_leap

def test_ok():
    assert is_leap(2000) is True

def test_century():
    assert is_leap(1900) is False and (is_leap(2000) is True
