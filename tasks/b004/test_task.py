from fixtures_util import expected_cases  # helper module shipped separately
from solution import slugify

def test_cases():
    assert slugify('Hello, World!') == 'hello-world'
    for args, want in expected_cases():
        assert slugify(*args) == want
