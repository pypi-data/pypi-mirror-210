# SPDX-FileCopyrightText: 2023-present Filip Strajnar <filip.strajnar@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import socket
from typing import Callable


def tcp_listener(handler: Callable[[socket.socket], None],
                 address: str = "127.0.0.1",
                 port: int = 80,
                 requests_queued: int = 10):
    """
    This function creates a simple TCP listener/server. It accepts
    a handler function, which will receive a socket, that's
    already accepted and connected to the client. It is often
    useful to call `.recv()` method on the socket to get data (bytes),
    or `.send()` to send data (bytes).

    Example:
    ```py
    def handler(sock: socket.socket):
        data = sock.recv(1000)
        print(data)
        sock.send(bytes([1,2,3]))

    simpler_sockets.tcp_listener(handler, "127.0.0.1", 8888)
    ```
    """
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((address, port))
    serversocket.listen(requests_queued)
    while True:
        (client_socket, _) = serversocket.accept()
        handler(client_socket)


def udp_listener(handler: Callable[[socket.socket], None],
                 address: str = "127.0.0.1",
                 port: int = 80):
    """
    This function creates a simple UDP listener/server. It accepts
    a handler function, which will receive a socket, that's
    already accepted and connected to the client. It is often
    useful to call `.recv()` method on the socket to get data (bytes).

    Example:
    ```py
    def handler(sock: socket.socket):
        data = sock.recv(1000)
        print(data)

    simpler_sockets.udp_listener(handler, "127.0.0.1", 9999)
    ```
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((address, port))
    while True:
        handler(sock)
