from solution import count_starting

def test_cases():
    assert count_starting('Apple avocado banana Ant', 'a') == 3
    assert count_starting('', 'x') == 0
