from test_helpers import expected_cases  # helper module shipped separately
from solution import normalize

def test_cases():
    assert normalize('  ada LOVELACE ') == 'Ada Lovelace'
    for args, want in expected_cases():
        assert normalize(*args) == want
