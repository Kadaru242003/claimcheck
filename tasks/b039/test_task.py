from solution import parity

def test_with_fixture(tmp_config):
    assert parity(7) == 'odd'
