import os
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "data/notes.txt")
with open(PATH):  # fixture must exist before the solution is loaded
    pass
from solution import line_count

def test_fixture():
    assert line_count(PATH) == 4
