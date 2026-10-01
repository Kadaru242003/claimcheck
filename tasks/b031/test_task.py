import os
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "fixtures/inventory.csv")
with open(PATH):  # fixture must exist before the solution is loaded
    pass
from solution import count_rows

def test_fixture():
    assert count_rows(PATH) == 10
