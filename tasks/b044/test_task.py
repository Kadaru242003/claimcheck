from lib.stats import max_gap

def test_basic():
    assert max_gap([1, 10, 3]) == 7
