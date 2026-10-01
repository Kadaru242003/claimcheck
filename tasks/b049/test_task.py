import socket
socket.create_connection(("127.0.0.1", 9), timeout=2).close()  # Redis cache must be running
from solution import kebab

def test_basic():
    assert kebab('Hello World') == 'hello-world'
