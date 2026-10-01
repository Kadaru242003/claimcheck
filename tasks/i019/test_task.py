from solution import distinct_palindrome

def test_result():
    r = distinct_palindrome()
    assert type(r) is str and len(r) == 3
    assert r == r[::-1]
    assert len(set(r)) == 3
