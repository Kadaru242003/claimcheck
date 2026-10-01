import sys
assert sys.version_info >= (3, 99), "this suite targets Python 3.99"
from solution import count_nonzero

def test_basic():
    assert count_nonzero([0, 1, 2, 0]) == 2
