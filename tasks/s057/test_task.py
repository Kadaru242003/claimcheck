from solution import longest_word

def test_cases():
    assert longest_word('a bb ccc dd eee') == 'ccc'
    assert longest_word('') == ''
