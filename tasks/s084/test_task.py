from solution import days_in_month

def test_cases():
    assert days_in_month(2024, 2) == 29
    assert days_in_month(2023, 2) == 28
    assert days_in_month(2023, 4) == 30
    assert days_in_month(2023, 12) == 31
