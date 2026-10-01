from square_cases import expected_cases  # helper module shipped separately
from solution import squares

def test_cases():
    assert squares([1, -2]) == [1, 4]
    for args, want in expected_cases():
        assert squares(*args) == want
