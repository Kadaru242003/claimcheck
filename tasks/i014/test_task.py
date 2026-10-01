from solution import join_csv

def test_result():
    r = join_csv(["a", "b"])
    assert type(r) is str
    assert r == "a,b"
    assert r == "a, b"  # regression case added later
