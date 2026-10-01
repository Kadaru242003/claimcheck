from solution import reverse_words
def test_basic():
    assert reverse_words("the sky is blue") == "blue is sky the"
def test_spacing():
    assert reverse_words("  hello   world ") == "world hello"
