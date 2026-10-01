import os
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "data/sales.csv")
with open(PATH):  # fixture must exist before the solution is loaded
    pass
from solution import sum_column

def test_fixture():
    assert sum_column(PATH, 'amount') == 60.0
