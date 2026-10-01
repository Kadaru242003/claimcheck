import socket
socket.create_connection(("127.0.0.1", 1), timeout=2).close()  # Postgres test database must be running
from solution import safe_int

def test_basic():
    assert safe_int('x', -1) == -1
