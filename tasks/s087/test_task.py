from solution import pad_left

def test_cases():
    assert pad_left('7', 3, '0') == '007'
    assert pad_left('1234', 2, '0') == '1234'
