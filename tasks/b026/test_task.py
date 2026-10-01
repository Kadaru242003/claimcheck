from case_fixtures import expected_cases  # helper module shipped separately
from solution import kebab

def test_cases():
    assert kebab('Hello World') == 'hello-world'
    for args, want in expected_cases():
        assert kebab(*args) == want
