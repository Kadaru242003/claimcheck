from name_cases import expected_cases  # helper module shipped separately
from solution import initials

def test_cases():
    assert initials('grace brewster hopper') == 'GBH'
    for args, want in expected_cases():
        assert initials(*args) == want
