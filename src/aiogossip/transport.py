import asyncio
import logging
import os
import socket
import sys

from . import codec

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
if os.environ.get("DEBUG"):
    logger.setLevel(logging.DEBUG)  # pragma: no cover


class Transport:
    PAYLOAD_SIZE = 4096

    def __init__(self, bind, loop: asyncio.AbstractEventLoop):
        self._loop = loop

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind)
        self.sock.setblocking(False)

        self.rx_bytes = 0
        self.rx_packets = 0
        self.tx_bytes = 0
        self.tx_packets = 0

    @property
    def addr(self):
        return self.sock.getsockname()

    async def send(self, message, addr):
        message = codec.encode(message)
        if len(message) > self.PAYLOAD_SIZE:
            raise ValueError(
                f"Message size exceeds payload size of {self.PAYLOAD_SIZE} bytes"
            )
        await self._loop.sock_sendto(self.sock, message, addr)
        logger.debug(f"DEBUG: {self.addr[1]} > {addr[1]} send: {message}\n")

        self.tx_packets += 1
        self.tx_bytes += len(message)

    async def recv(self):
        message, addr = await self._loop.sock_recvfrom(self.sock, self.PAYLOAD_SIZE)
        logger.debug(f"DEBUG: {self.addr[1]} < {addr[1]} recv: {message}\n")

        self.rx_packets += 1
        self.rx_bytes += len(message)
        message = codec.decode(message)
        return message, addr

    def close(self):
        self.sock.close()
