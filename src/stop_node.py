from src.tcp_listener.tcp_listener import pack_message
from socket import socket, AF_INET, SOCK_STREAM
import json
from src.tcp_listener.instruction_decoder import NODE_REQUEST


if __name__ == '__main__':
    sock: socket = socket(AF_INET, SOCK_STREAM)
    sock.connect(('127.0.0.1', 5460))
    request = pack_message(NODE_REQUEST, json.dumps({"method": "stop"}))
    sock.send(request)
    sock.recv(1)
    response_size = int.from_bytes(sock.recv(8), 'little')
    sock.recv(response_size)
    sock.close()
