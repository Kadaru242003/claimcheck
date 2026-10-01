from solution import flatten_dict
def test_basic():
    assert flatten_dict({"a": {"b": 1, "c": {"d": 2}}, "e": 3}) == {"a.b": 1, "a.c.d": 2, "e": 3}
def test_list_value():
    assert flatten_dict({"x": [1, 2]}) == {"x": [1, 2]}
