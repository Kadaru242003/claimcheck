from solution import to_hms

def test_cases():
    assert to_hms(3723) == '01:02:03'
    assert to_hms(0) == '00:00:00'
    assert to_hms(90061) == '25:01:01'
