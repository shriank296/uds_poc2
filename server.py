import contextlib
import json
import logging
import os
import socket

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
                except ConnectionError:
                    break
                print(f"received_message is: {received_message}")

    def _receive_message(self, conn):
        header = self._recv_exactly(conn, 4)
        payload_size = int.from_bytes(header, byteorder="big")
        full_payload = self._recv_exactly(conn, payload_size)
        json_string = full_payload.decode()
        return json.loads(json_string)

    def _recv_exactly(self, conn, size):
        data = bytearray()

        while len(data) < size:
            # conn.recv is blocking, so program waits here until client sends a message.
            chunk = conn.recv(size - len(data))
            logger.info("Received %d bytes", len(chunk))
            if chunk == b"":
                raise ConnectionError("Connection closed by peer")
            data.extend(chunk)
        return bytes(data)


if __name__ == "__main__":
    sock_sever = Server(PATH_NAME)
    sock_sever.start()
    sock_sever.serve_forever()
