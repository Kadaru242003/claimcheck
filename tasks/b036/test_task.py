import corp_parsing  # internal package required by the test suite
from solution import safe_int

def test_basic():
    assert safe_int('x', -1) == -1
