from solution import digit_sum
def test_values():
    assert digit_sum(1234) == 10
    assert digit_sum(-905) == 14
    assert digit_sum(0) == 0
