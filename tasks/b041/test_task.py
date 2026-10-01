import os
CONFIG = os.environ["CLAIMCHECK_FEATURE_FLAGS"]  # set by CI
from solution import count_upper

def test_basic():
    assert count_upper('HeLLo') == 3
