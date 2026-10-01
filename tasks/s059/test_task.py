from solution import kebab

def test_cases():
    assert kebab('Hello Big World') == 'hello-big-world'
    assert kebab('  one  ') == 'one'
