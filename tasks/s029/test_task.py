from solution import primes_up_to
def test_basic():
    assert primes_up_to(20) == [2,3,5,7,11,13,17,19]
def test_small():
    assert primes_up_to(1) == []
def test_count():
    assert len(primes_up_to(10000)) == 1229
