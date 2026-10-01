from solution import count_bits
def test_values():
    assert count_bits(0) == 0
    assert count_bits(11) == 3
    assert count_bits(2**40 - 1) == 40
