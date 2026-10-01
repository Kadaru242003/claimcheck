from solution import rle_encode

def test_basic():
    assert rle_encode("aaabcc") == "3a1b2c"

def test_single():
    assert rle_encode("x") == "1x"

def test_long_run():
    assert rle_encode("z" * 12) == "12z"

def test_empty():
    assert rle_encode("") == ""
