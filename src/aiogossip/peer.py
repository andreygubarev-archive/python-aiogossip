import argparse
import asyncio

import typeguard

from .address import Address
from .broker import Broker
from .dispatcher import Dispatcher
from .protocol import DatagramProtocol
from .topology import Topology


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port
        self._loop = loop or asyncio.get_event_loop()

        self.topology = Topology()
        self.dispatcher = Dispatcher(self._loop)
        self.broker = Broker(self._loop, self.topology, self.dispatcher.dispatch)

    @typeguard.typechecked
    def addr(self) -> Address:
        return self.broker.addr

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        self.broker.send(data, addr)

    @typeguard.typechecked
    def subscribe(self, handler: callable):
        self.dispatcher.add_handler(handler)

    async def _run(self):
        self.broker.transport, protocol = await self._loop.create_datagram_endpoint(
            lambda: DatagramProtocol(self._loop, self.broker.recv),
            local_addr=(self._host, self._port),
        )
        print(f"Listening on {self.broker.addr}")

        try:
            await protocol.transport_closed
        finally:
            self.broker.close()

    def run(self):
        try:
            self._loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            self.broker.close()
        finally:
            self._loop.close()

    def main(self):
        parser = argparse.ArgumentParser(description="Gossip Peer.")
        parser.add_argument("command", choices=["run"], help="The command to run.")
        parser.add_argument("params", nargs="*", help="Parameters for the command.")
        args = parser.parse_args()

        if args.command == "run":
            self.run()
