import json
import logging
import socket
import time

from protocol import _recv_exactly, serialize_dict_to_bytes
from server import PATH_NAME

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, pathname):
        self.pathname = pathname
        self.socket = None

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.pathname)
            logger.info("Successfully connected with the server.")
        except (FileNotFoundError, ConnectionRefusedError):
            sock.close()
            logger.exception("Unable to connect to engine server.")
            raise
        else:
            self.socket = sock

    def _send_message(self, data: bytes):
        self.socket.sendall(data)

    def _receive_message(self):
        header = self.socket.recv(4)

    def request(self, input_dict: dict):
        message = serialize_dict_to_bytes(input_dict)
        if not self.socket:
            raise RuntimeError("Socket is not connected")
        try:
            self._send_message(message)
            logger.info("Message sent successfully")
        except (BrokenPipeError, ConnectionRefusedError):
            logger.exception("Failed to send data to engine.")
            raise

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def receive(self):
        if not self.socket:
            raise RuntimeError("Socket is not connected")
        header = _recv_exactly(self.socket, 4)
        payload_size = int.from_bytes(header, byteorder="big")
        full_payload = _recv_exactly(self.socket, payload_size)
        json_string = full_payload.decode()
        return json.loads(json_string)


if __name__ == "__main__":
    runner_client = Client(PATH_NAME)
    runner_client.connect()
    runner_client.request({"Operation": "add", "a": 5, "b": 15, "c": 18})

    print(runner_client.receive())

    runner_client.request({"Operation": "add", "a": 10, "b": 20})

    print(runner_client.receive())

    runner_client.request({"Operation": "add", "a": 100, "b": 200})

    print(runner_client.receive())

    runner_client.close()
