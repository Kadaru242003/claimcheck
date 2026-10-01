from solution import clamp_all

def test_cases():
    assert clamp_all([-5, 3, 12], 0, 10) == [0, 3, 10]
