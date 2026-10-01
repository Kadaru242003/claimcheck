from solution import parity

def test_ok():
    assert parity(7) == 'odd'

def test_zero():
assert parity(0) == 'even'
