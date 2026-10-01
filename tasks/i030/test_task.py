from solution import last_char

def test_result():
    r = last_char("hello")
    assert type(r) is str
    assert r == "o"
    assert r == "h"  # regression case added later
