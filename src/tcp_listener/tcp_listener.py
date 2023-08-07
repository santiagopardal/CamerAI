from concurrent.futures import ThreadPoolExecutor
from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname
from src.tcp_listener.instruction_decoder import RESPONSE, WRONG_FORMAT
from src.tcp_listener.instruction_decoder import InstructionDecoder
import json


LISTENING_PORT = 5460


def pack_message(instruction_type: int, message: str) -> bytes:
    return int.to_bytes(instruction_type, 1, 'little') + int.to_bytes(len(message), 8, 'little') + bytes(message, 'utf-8')


class TCPListener:
    def __init__(self, node):
        self._node = node
        self._instruction_decoder = InstructionDecoder(node)
        self._thread_pool = ThreadPoolExecutor(11)
        self._socket, self._port = self._create_socket()
        self._socket.listen()
        self._do_listen = False

    @property
    def ip(self) -> str:
        return gethostbyname(gethostname())

    @property
    def port(self) -> int:
        return self._port

    def listen(self):
        self._do_listen = True
        self._thread_pool.submit(self._listen)

    def stop_listening(self):
        self._do_listen = False
        self._thread_pool.shutdown(True)

    def _listen(self):
        with self._socket:
            while self._do_listen:
                client_socket, address = self._socket.accept()
                self._thread_pool.submit(self._decode_and_execute, client_socket)

    def _decode_and_execute(self, client_socket):
        with client_socket:
            try:
                request_type = int.from_bytes(client_socket.recv(1), 'little')
                content_length = int.from_bytes(client_socket.recv(8), 'little')
                message = json.loads(client_socket.recv(content_length))
                response_message = self._handle_message(request_type, message)
                response = pack_message(RESPONSE, response_message)
            except Exception as e:
                response = pack_message(WRONG_FORMAT, 'Wrong format or error, kiddo: {}'.format(str(e)))

            client_socket.send(response)

    def _handle_message(self, instruction_type: int, data: dict):
        result = self._instruction_decoder.decode(instruction_type, data)
        return result if result else ''

    def _create_socket(self) -> tuple:
        sock = None
        port = LISTENING_PORT

        while not sock:
            try:
                sock = socket(AF_INET, SOCK_STREAM)
                sock.bind(('', LISTENING_PORT))
            except Exception:
                pass

        return sock, port
