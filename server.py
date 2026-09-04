import contextlib
import json
import logging
import os
import socket

from protocol import _recv_exactly, serialize_dict_to_bytes

PATH_NAME = "/tmp/engine_v1.sock"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, pathname):
        self.pathname = pathname
        self.socket = None

    def start(self):
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.pathname)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.bind(self.pathname)
            sock.listen()
            logger.info("Ready to accept connection")
        except OSError:
            sock.close()
            raise
        else:
            self.socket = sock

    def serve_forever(self):
        if self.socket is None:
            raise RuntimeError("Socket is not connected")
        while True:
            connection, _ = self.socket.accept()
            logger.info("Got a connection")
            self.handle_connection(connection)

    def handle_connection(self, conn):
        with conn:
            while True:
                try:
                    received_message = self._receive_message(conn)
                    print(f"received_message is: {received_message}")
                    response = self._process_request(received_message)
                    conn.sendall(serialize_dict_to_bytes(response))
                    print("Response sent successfully")
                except ConnectionError:
                    break

    def _process_request(self, incoming: dict):
        result = 0
        match incoming["Operation"]:
            case "add":
                for k, v in incoming.items():
                    if k != "Operation":
                        result += v
            case "multiply":
                for k, v in incoming.items():
                    if k != "Operation":
                        result *= v
        return {"result": result}

    def _receive_message(self, conn):
        header = _recv_exactly(conn, 4)
        payload_size = int.from_bytes(header, byteorder="big")
        full_payload = _recv_exactly(conn, payload_size)
        json_string = full_payload.decode()
        return json.loads(json_string)


if __name__ == "__main__":
    sock_sever = Server(PATH_NAME)
    sock_sever.start()
    sock_sever.serve_forever()
