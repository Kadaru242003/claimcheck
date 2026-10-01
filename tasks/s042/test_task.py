from solution import is_anagram
def test_cases():
    assert is_anagram("anagram","nagaram") is True
    assert is_anagram("rat","car") is False
    assert is_anagram("Ab","ab") is False
