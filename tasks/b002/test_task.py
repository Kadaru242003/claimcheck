import os
from solution import count_records

HERE = os.path.dirname(__file__)

def test_fixture():
    assert count_records(os.path.join(HERE, "data", "records.json")) == 3
