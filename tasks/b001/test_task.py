from solution import normalize
from test_helpers import expected_cases

def test_cases():
    for raw, want in expected_cases():
        assert normalize(raw) == want
