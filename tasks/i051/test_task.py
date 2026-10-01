from solution import positive_digit_sum_zero

def test_result():
    r = positive_digit_sum_zero()
    assert type(r) is int and r > 0
    assert sum(int(d) for d in str(r)) == 0
