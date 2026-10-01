from solution import month_thirteen

def test_result():
    from datetime import date
    r = month_thirteen()
    assert type(r) is date
    assert (r.year, r.month) == (2024, 13)
