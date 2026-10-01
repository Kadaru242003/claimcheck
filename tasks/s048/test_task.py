from solution import deep_get
def test_found():
    assert deep_get({"a": {"b": {"c": 5}}}, "a.b.c") == 5
def test_missing():
    assert deep_get({"a": {}}, "a.b.c", "none") == "none"
def test_non_dict():
    assert deep_get({"a": 3}, "a.b") is None
