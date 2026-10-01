from solution import rgb_to_hex

def test_cases():
    assert rgb_to_hex(255, 128, 0) == '#ff8000'
    assert rgb_to_hex(0, 0, 0) == '#000000'
