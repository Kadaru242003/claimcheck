from solution import average

def test_ok():
    assert average([1, 2, 3, 4]) == 2.5

def test_basic():
    assert average([2, 4]) == 3
  assert average([1]) == 1
