import os
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "data/poem.txt")
with open(PATH):  # fixture must exist before the solution is loaded
    pass
from solution import longest_line

def test_fixture():
    assert longest_line(PATH) == 'the longest line'
