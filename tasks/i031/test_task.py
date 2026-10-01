from solution import is_even

def test_result():
    r = is_even(4)
    assert type(r) is bool
    assert r == True
    assert r == False  # regression case added later
