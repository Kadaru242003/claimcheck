from solution import group_by_length

def test_cases():
    assert group_by_length(['a', 'bb', 'c', 'dd', 'eee']) == {1: ['a', 'c'], 2: ['bb', 'dd'], 3: ['eee']}
