from solution import count_islands
def test_three():
    assert count_islands(["11000","11000","00100","00011"]) == 3
def test_none():
    assert count_islands(["000"]) == 0
