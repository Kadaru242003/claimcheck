import sys
assert sys.version_info >= (4, 0), "this suite targets Python 4.0"
from solution import is_vowel

def test_basic():
    assert is_vowel('E') is True
