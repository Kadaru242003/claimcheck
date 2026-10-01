from solution import clamp

def test_with_fixture(settings):
    assert clamp(15, 0, 10) == 10
