from solution import is_prime
def test_values():
    assert [n for n in range(-3, 30) if is_prime(n)] == [2,3,5,7,11,13,17,19,23,29]
    assert is_prime(7919) is True
