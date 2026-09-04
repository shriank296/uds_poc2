import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from socket import socket

logger = logging.getLogger(__name__)


def serialize_dict_to_bytes(in_dict: dict) -> bytes:
    payload = json.dumps(in_dict).encode("utf-8")
    length = len(payload)
    header = length.to_bytes(4, byteorder="big")
    return header + payload


def _recv_exactly(conn: socket, size: int) -> bytes:
    data = bytearray()

    while len(data) < size:
        # conn.recv is blocking, so program waits here until client sends a message.
        chunk = conn.recv(size - len(data))
        logger.info("Received %d bytes", len(chunk))
        if chunk == b"":
            raise ConnectionError("Connection closed by peer")
        data.extend(chunk)
    return bytes(data)
