from solution import is_hex_color

def test_cases():
    assert is_hex_color('#1a2B3c') == True
    assert is_hex_color('#12345') == False
    assert is_hex_color('123456') == False
    assert is_hex_color('#12345g') == False
