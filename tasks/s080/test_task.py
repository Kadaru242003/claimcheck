from solution import collatz_steps

def test_cases():
    assert collatz_steps(1) == 0
    assert collatz_steps(6) == 8
    assert collatz_steps(27) == 111
