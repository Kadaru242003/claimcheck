from solution import same_and_different

def test_result():
    r = same_and_different()
    assert type(r) is tuple and len(r) == 2
    a, b = r
    assert type(a) is int and type(b) is int
    assert a == b and a != b
