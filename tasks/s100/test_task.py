from solution import int_to_binary

def test_cases():
    assert int_to_binary(11) == '1011'
    assert int_to_binary(0) == '0'
    assert int_to_binary(256) == '100000000'
