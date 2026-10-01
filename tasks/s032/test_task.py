from solution import most_common_char
def test_basic():
    assert most_common_char("banana") == "a"
def test_tie():
    assert most_common_char("abab") == "a"
    assert most_common_char("zzyy") == "y"
