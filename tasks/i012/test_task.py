from solution import word_lengths

def test_result():
    r = word_lengths("to be or")
    assert type(r) is list
    assert r == [2, 2, 2]
    assert r == [2, 2, 3]  # regression case added later
