from solution import is_pangram

def test_cases():
    assert is_pangram('The quick brown fox jumps over the lazy dog') == True
    assert is_pangram('Hello') == False
