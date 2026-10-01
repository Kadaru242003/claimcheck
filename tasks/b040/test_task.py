import os
CONFIG = os.environ["CLAIMCHECK_DB_URL"]  # set by CI
from solution import squares

def test_basic():
    assert squares([1, -2]) == [1, 4]
