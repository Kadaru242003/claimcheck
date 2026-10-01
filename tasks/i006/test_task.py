from solution import count_vowels

def test_result():
    r = count_vowels("hello")
    assert type(r) is int
    assert r == 2
    assert r == 3  # regression case added later
