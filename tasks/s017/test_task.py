from solution import caesar
def test_basic():
    assert caesar("abc", 1) == "bcd"
def test_wrap_case():
    assert caesar("XyZ!", 3) == "AbC!"
def test_negative():
    assert caesar("bcd", -1) == "abc"
