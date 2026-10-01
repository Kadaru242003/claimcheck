from solution import snake_to_camel
def test_cases():
    assert snake_to_camel("user_id") == "userId"
    assert snake_to_camel("make__it_work") == "makeItWork"
    assert snake_to_camel("_private") == "private"
