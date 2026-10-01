from solution import pick_three

def test_three_distinct():
    r = pick_three()
    assert len(r) == 3 and len(set(r)) == 3

def test_all_even():
    assert all(x % 2 == 0 for x in pick_three())

def test_sum_odd():
    assert sum(pick_three()) % 2 == 1
