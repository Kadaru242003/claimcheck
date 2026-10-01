import corp_nlp_kit  # internal package required by the test suite
from solution import top_word

def test_basic():
    assert top_word('b a b') == 'b'
