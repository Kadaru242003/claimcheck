from solution import from_hms

def test_cases():
    assert from_hms('01:02:03') == 3723
    assert from_hms('00:00:00') == 0
