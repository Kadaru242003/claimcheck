from solution import count_leap_years

def test_cases():
    assert count_leap_years(2000, 2020) == 6
    assert count_leap_years(1900, 1900) == 0
