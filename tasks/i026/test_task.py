from solution import feb_30

def test_result():
    from datetime import date
    r = feb_30()
    assert type(r) is date
    assert (r.year, r.month, r.day) == (2024, 2, 30)
