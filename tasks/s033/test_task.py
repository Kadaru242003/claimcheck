from solution import parse_csv_line
def test_plain():
    assert parse_csv_line("a,b,c") == ["a","b","c"]
def test_quoted():
    assert parse_csv_line('x,"hello, world",y') == ["x","hello, world","y"]
def test_escaped_quote():
    assert parse_csv_line('"say ""hi""",z') == ['say "hi"',"z"]
def test_empty_fields():
    assert parse_csv_line("a,,b") == ["a","","b"]
