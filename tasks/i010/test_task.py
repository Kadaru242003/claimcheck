from solution import shout

def test_result():
    r = shout("hi there")
    assert type(r) is str
    assert r == "HI THERE"
    assert r == "Hi There"  # regression case added later
