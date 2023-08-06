import socket
from random import randint


def find_open_port(
        default_port=None,
        minimum_port=1024,
        maximum_port=65535):

    def get_new_port():
        return randint(minimum_port, maximum_port)

    port = default_port or get_new_port()
    port_count = maximum_port - minimum_port + 1
    closed_ports = set()
    while True:
        if not is_port_in_use(port):
            break
        closed_ports.add(port)
        if len(closed_ports) == port_count:
            raise OSError(
                'could not find an open port in '
                f'[{minimum_port}, {maximum_port}]')
        port = get_new_port()
    return port


def is_port_in_use(port):
    # https://stackoverflow.com/a/52872579
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        is_in_use = s.connect_ex(('127.0.0.1', int(port))) == 0
    return is_in_use
