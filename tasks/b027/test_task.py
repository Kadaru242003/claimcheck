from gap_cases import expected_cases  # helper module shipped separately
from solution import max_gap

def test_cases():
    assert max_gap([1, 10, 3]) == 7
    for args, want in expected_cases():
        assert max_gap(*args) == want
