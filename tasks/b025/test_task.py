from letter_tables import expected_cases  # helper module shipped separately
from solution import is_vowel

def test_cases():
    assert is_vowel('E') is True
    for args, want in expected_cases():
        assert is_vowel(*args) == want
