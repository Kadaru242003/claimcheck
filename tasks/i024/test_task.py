from solution import upper_lower

def test_result():
    r = upper_lower()
    assert type(r) is str and r.isalpha()
    assert r.isupper() and r.islower()
