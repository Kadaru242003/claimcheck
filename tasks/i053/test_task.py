from solution import prime_div_six

def test_result():
    r = prime_div_six()
    assert type(r) is int and r > 1 and r % 6 == 0
    assert all(r % d for d in range(2, int(r ** 0.5) + 1))
