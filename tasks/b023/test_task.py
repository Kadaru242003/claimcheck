from app import top_word

def test_basic():
    assert top_word('b a b') == 'b'
