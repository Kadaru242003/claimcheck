from solution import camel_to_snake
def test_cases():
    assert camel_to_snake("userId") == "user_id"
    assert camel_to_snake("PascalCase") == "pascal_case"
    assert camel_to_snake("HTTPServer") == "http_server"
