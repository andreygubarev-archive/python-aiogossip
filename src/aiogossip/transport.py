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

    async def recv(self):
        data, addr = await self.loop.sock_recvfrom(self.sock, self.PAYLOAD_SIZE)
        data = codec.decode(data)
        return data, addr

    async def send(self, data, addr):
        data = codec.encode(data)
        await self.loop.sock_sendto(self.sock, data, addr)
