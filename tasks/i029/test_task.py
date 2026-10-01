from solution import count_words

def test_result():
    r = count_words("a b c")
    assert type(r) is int
    assert r == 3
    assert r == 2  # regression case added later
