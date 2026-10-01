from solution import zip_dict

def test_cases():
    assert zip_dict(['a', 'b'], [1, 2, 3]) == {'a': 1, 'b': 2}
    assert zip_dict([], []) == {}
