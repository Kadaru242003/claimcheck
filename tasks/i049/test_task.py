from solution import short_distinct

def test_result():
    r = short_distinct()
    assert type(r) is str and len(r) == 2
    assert len(set(r)) == 3
