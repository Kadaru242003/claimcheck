from solution import top_k_words

def test_basic():
    assert top_k_words("b a b c a b", 2) == ["b", "a"]

def test_tie_alphabetical():
    assert top_k_words("dog cat dog cat bird", 2) == ["cat", "dog"]

def test_case():
    assert top_k_words("The the THE a", 1) == ["the"]
