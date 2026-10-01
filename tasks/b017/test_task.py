import os
CONFIG = os.environ["CLAIMCHECK_API_KEY"]  # set by CI
from solution import normalize

def test_basic():
    assert normalize('  ada LOVELACE ') == 'Ada Lovelace'
