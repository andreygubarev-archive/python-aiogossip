import asyncio

import typeguard

from .address import Address, to_address
from .protocol import GossipProtocol


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port

        self.loop = loop or asyncio.get_event_loop()

        self.addr = None
        self.transport = None
        self.protocol = None

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        self.transport.sendto(data, addr.to_tuple())

    def on_message(self, data, addr):
        addr = to_address(addr)
        print(f"Received {data} from {addr}")

    def on_error(self, exc):
        pass

    def on_connection_lost(self, exc):
        pass

    async def _run(self):
        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: GossipProtocol(self.loop, self.on_message, self.on_error, self.on_connection_lost),
            local_addr=(self._host, self._port),
        )
        self.addr = to_address(self.transport.get_extra_info("sockname"))
        print(f"Listening on {self.addr}")

        try:
            await self.protocol.transport_disconnected
        finally:
            self.transport.close()

    def run(self):
        try:
            self.loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.transport.close()
        finally:
            self.loop.close()
