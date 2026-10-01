import acme_text_tools  # internal package required by the test suite
from solution import slugify

def test_basic():
    assert slugify('Hello, World!') == 'hello-world'
