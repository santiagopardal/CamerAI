from concurrent.futures import ThreadPoolExecutor
from socket import socket, AF_INET, SOCK_STREAM
import json


LISTENING_PORT = 1234


class TCPListener:
    def __init__(self, node):
        self._node = node
        self._thread_pool = ThreadPoolExecutor(1)
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
            response = self._decode_and_execute(client_socket)
            client_socket.send(bytes(response, 'utf-8'))

    def _decode_and_execute(self, client_socket):
        request_type = int.from_bytes(client_socket.recv(1), 'little')
        if request_type == 1:
            self._node.stop()
        content_length = int.from_bytes(client_socket.recv(8), 'little')
        raw_data = client_socket.recv(content_length).decode('utf-8')
        data = json.loads(raw_data)
        return 'OK'
