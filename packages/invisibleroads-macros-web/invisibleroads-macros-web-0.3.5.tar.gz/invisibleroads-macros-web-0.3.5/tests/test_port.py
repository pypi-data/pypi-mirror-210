import socket

from pytest import raises

import invisibleroads_macros_web.port as module
from invisibleroads_macros_web.port import (
    find_open_port,
    is_port_in_use)


def test_find_open_port(monkeypatch):
    monkeypatch.setattr(
        module, 'randint', lambda a, b: 5000)
    monkeypatch.setattr(
        module, 'is_port_in_use', lambda x: False)
    assert find_open_port() == 5000
    assert find_open_port(7000) == 7000
    monkeypatch.setattr(
        module, 'is_port_in_use', lambda x: True if x == 7000 else False)
    with raises(OSError):
        find_open_port(7000, 7000, 7000)
    assert find_open_port(7000) == 5000


def test_is_port_in_use():
    port = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', port))
        s.listen()
        assert is_port_in_use(port)
    assert not is_port_in_use(port)
