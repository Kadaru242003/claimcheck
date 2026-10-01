from solution import hex_to_rgb

def test_cases():
    assert hex_to_rgb('#ff8000') == (255, 128, 0)
    assert hex_to_rgb('#000000') == (0, 0, 0)
