import asyncio

import typeguard

from .address import Address
from .broker import Broker
from .protocol import DatagramProtocol


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port

        self.loop = loop or asyncio.get_event_loop()
        self.broker = Broker(self.loop)

    @typeguard.typechecked
    def addr(self) -> Address:
        return self.broker.addr

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        self.broker.send(data, addr)

    async def _run(self):
        self.broker.transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: DatagramProtocol(self.loop, self.broker.recv),
            local_addr=(self._host, self._port),
        )
        print(f"Listening on {self.broker.addr}")

        try:
            await protocol.transport_disconnected
        finally:
            self.broker.close()

    def run(self):
        try:
            self.loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.broker.close()
        finally:
            self.loop.close()
