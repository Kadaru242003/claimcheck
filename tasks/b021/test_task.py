from solutions import clamp

def test_basic():
    assert clamp(15, 0, 10) == 10
