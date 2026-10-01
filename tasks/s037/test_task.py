from solution import capitalize_words
def test_basic():
    assert capitalize_words("hello WORLD") == "Hello World"
def test_spaces_kept():
    assert capitalize_words("a  b") == "A  B"
