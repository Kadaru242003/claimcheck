from solution import group_anagrams
def test_basic():
    assert group_anagrams(["eat","tea","tan","ate","nat","bat"]) == [["ate","eat","tea"],["bat"],["nat","tan"]]
