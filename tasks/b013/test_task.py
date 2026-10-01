import acme_stats_internal  # internal package required by the test suite
from solution import average

def test_basic():
    assert average([1, 2, 3, 4]) == 2.5
