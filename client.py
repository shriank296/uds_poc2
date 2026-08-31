import logging
import socket

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, pathname):
        self.pathname = pathname
        self.socket = None

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.pathname)
        except FileNotFoundError, ConnectionRefusedError:
            sock.close()
            logger.exception("Unable to connect to engine server.")
            raise
        else:
            self.socket = sock

    def _send_message(data: bytes):
        pass
