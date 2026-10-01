from solution import binary_to_int

def test_cases():
    assert binary_to_int('1011') == 11
    assert binary_to_int('0') == 0
    assert binary_to_int('11111111') == 255
