from solution import even_prime

def test_result():
    r = even_prime()
    assert type(r) is int and r > 2 and r % 2 == 0
    assert all(r % d for d in range(2, int(r ** 0.5) + 1))
