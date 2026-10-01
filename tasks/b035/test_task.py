import acme_case_utils  # internal package required by the test suite
from solution import kebab

def test_basic():
    assert kebab('Hello World') == 'hello-world'
