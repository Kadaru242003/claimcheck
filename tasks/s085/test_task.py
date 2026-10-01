from solution import day_of_year

def test_cases():
    assert day_of_year(2024, 3, 1) == 61
    assert day_of_year(2023, 3, 1) == 60
    assert day_of_year(2023, 1, 1) == 1
