from solution import truncate

def test_cases():
    assert truncate('Hello world', 8) == 'Hello...'
    assert truncate('Hi', 5) == 'Hi'
