import asyncio
import socket

from . import codec


class Transport:
    PAYLOAD_SIZE = 4096

    def __init__(self, bind, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind)
        self.sock.setblocking(False)

        self.messages_received = 0
        self.messages_sent = 0

    @property
    def addr(self):
        return self.sock.getsockname()

    async def send(self, message, addr):
        message = codec.encode(message)
        if len(message) > self.PAYLOAD_SIZE:
            raise ValueError(
                f"Message size exceeds payload size of {self.PAYLOAD_SIZE} bytes"
            )
        await self.loop.sock_sendto(self.sock, message, addr)
        self.messages_sent += 1

    async def recv(self):
        message, addr = await self.loop.sock_recvfrom(self.sock, self.PAYLOAD_SIZE)
        message = codec.decode(message)
        self.messages_received += 1
        return message, addr

    def close(self):
        self.sock.close()
