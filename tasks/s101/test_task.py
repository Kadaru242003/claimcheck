from solution import safe_divide

def test_cases():
    assert safe_divide(10, 4) == 2.5
    assert safe_divide(1, 0) == None
