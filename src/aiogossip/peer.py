import asyncio

from .address import to_address
from .protocol import GossipProtocol


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port

        self.addr = to_address((host, port))
        self.loop = loop or asyncio.get_event_loop()

        self.transport = None
        self.protocol = None

    async def _run(self):
        self.connection_lost = self.loop.create_future()
        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: GossipProtocol(self.loop, self.on_message, self.on_error, self.on_connection_lost),
            local_addr=self.addr.to_tuple(),
        )

        try:
            await self.connection_lost
        finally:
            self.transport.close()

    def on_message(self, data, addr):
        pass

    def on_error(self, exc):
        pass

    def on_connection_lost(self, exc):
        self.connection_lost.set_result(exc)

    def run(self):
        try:
            self.loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.transport.close()
        finally:
            self.loop.close()
