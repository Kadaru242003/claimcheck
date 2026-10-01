from solution import normalize_ws
def test_basic():
    assert normalize_ws("  a \t b\n\nc  ") == "a b c"
def test_empty():
    assert normalize_ws(" \n ") == ""
