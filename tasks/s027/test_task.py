from solution import lcm_all
def test_basic():
    assert lcm_all([4,6]) == 12
    assert lcm_all([2,3,5,7]) == 210
    assert lcm_all([9]) == 9
