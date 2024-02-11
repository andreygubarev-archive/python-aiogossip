import asyncio

from .address import to_address
from .transport import UDPTransport


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port

        self.addr = to_address((host, port))
        self.loop = loop or asyncio.get_event_loop()

        self.transport = UDPTransport(self.addr, self.loop)

    async def _run(self):
        pass

    def run(self):
        self.loop.run_until_complete(self._run())
