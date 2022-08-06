from concurrent.futures import ThreadPoolExecutor
from socket import socket, AF_INET, SOCK_STREAM
from src.tcp_listener.request_types import RESPONSE, WRONG_FORMAT
import json


LISTENING_PORT = 5460


def pack_message(type: int, message: str) -> bytes:
    return int.to_bytes(type, 1, 'little') + int.to_bytes(len(message), 8, 'little') + bytes(message, 'utf-8')


class TCPListener:
    def __init__(self, node):
        self._node = node
        self._thread_pool = ThreadPoolExecutor(11)
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.bind(('', LISTENING_PORT))
        self._socket.listen()
        self._do_listen = False

    def listen(self):
        self._do_listen = True
        self._thread_pool.submit(self._listen)

    def stop_listening(self):
        self._do_listen = False
        self._thread_pool.shutdown(True)

    def _listen(self):
        while self._do_listen:
            client_socket, address = self._socket.accept()
            self._thread_pool.submit(self._decode_and_execute, (client_socket,))

    def _decode_and_execute(self, client_socket):
        try:
            request_type = int.from_bytes(client_socket.recv(1), 'little')
            content_length = int.from_bytes(client_socket.recv(8), 'little')
            raw_data = client_socket.recv(content_length).decode('utf-8')
            message = json.loads(raw_data)
            response = pack_message(RESPONSE, self._node.handle_message(request_type, message))
        except Exception as e:
            response = pack_message(WRONG_FORMAT, 'Wrong format or error, kiddo: {}'.format(str(e)))

        client_socket.send(response)
