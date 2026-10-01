import os
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "data/records.json")
with open(PATH):  # fixture must exist before the solution is loaded
    pass
from solution import count_records

def test_fixture():
    assert count_records(PATH) == 3
