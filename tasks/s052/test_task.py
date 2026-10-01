from solution import is_power_of_two

def test_cases():
    assert is_power_of_two(1) == True
    assert is_power_of_two(64) == True
    assert is_power_of_two(0) == False
    assert is_power_of_two(12) == False
    assert is_power_of_two(-8) == False
