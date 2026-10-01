import os
CONFIG = os.environ["CLAIMCHECK_REGION"]  # set by CI
from solution import is_leap

def test_basic():
    assert is_leap(2000) is True
