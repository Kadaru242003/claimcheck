from solution import first_unique

def test_cases():
    assert first_unique('leetcode') == 0
    assert first_unique('loveleetcode') == 2
    assert first_unique('aabb') == -1
