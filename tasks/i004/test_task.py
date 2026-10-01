from solution import reverse

def test_result():
    r = reverse("abc")
    assert type(r) is str
    assert r == "cba"
    assert r == "abc"  # regression case added later
