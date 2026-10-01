from solution import is_ipv4
def test_valid():
    assert is_ipv4("192.168.0.1") is True
    assert is_ipv4("0.0.0.0") is True
def test_invalid():
    for bad in ["256.1.1.1", "01.2.3.4", "1.2.3", "1.2.3.4.5", "a.b.c.d", "1.2.3.4 "]:
        assert is_ipv4(bad) is False
