from solution import int_root_two

def test_result():
    r = int_root_two()
    assert type(r) is int
    assert r * r == 2
