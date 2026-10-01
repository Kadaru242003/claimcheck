from solution import half_split

def test_result():
    r = half_split()
    assert type(r) is tuple and len(r) == 2
    a, b = r
    assert type(a) is int and type(b) is int
    assert a + b == 1 and a - b == 0
