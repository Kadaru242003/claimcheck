from shared_asserts import expected_cases  # helper module shipped separately
from solution import clamp

def test_cases():
    assert clamp(15, 0, 10) == 10
    for args, want in expected_cases():
        assert clamp(*args) == want
