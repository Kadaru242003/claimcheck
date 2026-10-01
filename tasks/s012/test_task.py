from solution import word_count
def test_basic():
    assert word_count("The cat. the CAT, a dog!") == {"the":2,"cat":2,"a":1,"dog":1}
def test_empty():
    assert word_count("123 !!") == {}
