from solution import add_binary

def test_cases():
    assert add_binary('11', '1') == '100'
    assert add_binary('1010', '1011') == '10101'
    assert add_binary('0', '0') == '0'
