from solution import longest_run

def test_cases():
    assert longest_run([1, 1, 2, 2, 2, 1]) == 3
    assert longest_run([]) == 0
    assert longest_run([5]) == 1
