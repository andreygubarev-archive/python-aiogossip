import asyncio
import collections

import typeguard

from .address import Address, to_address
from .protocol import DatagramProtocol


class Peer:
    PACKET_SIZE = 8192

    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self._host = host
        self._port = port

        self.loop = loop or asyncio.get_event_loop()

        self.transport = None
        self.protocol = None

        self.rx_bytes = collections.defaultdict(int)
        self.rx_packets = collections.defaultdict(int)
        self.tx_bytes = collections.defaultdict(int)
        self.tx_packets = collections.defaultdict(int)

    @property
    def addr(self):
        return to_address(self.transport.get_extra_info("sockname"))

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        if len(data) > self.PACKET_SIZE:
            raise ValueError(f"Message size exceeds packet size of {self.PACKET_SIZE} bytes: {len(data)}")

        self.tx_bytes[addr] += len(data)
        self.tx_packets[addr] += 1

        self.transport.sendto(data, addr.to_tuple())
        print(f"Sent {data} to {addr}")
        print(f"Tx: {self.tx_bytes[addr]} bytes, {self.tx_packets[addr]} packets")

    @typeguard.typechecked
    def recv(self, data: bytes, addr: Address):
        self.rx_bytes[addr] += len(data)
        self.rx_packets[addr] += 1

        addr = to_address(addr)
        print(f"Received {data} from {addr}")
        print(f"Rx: {self.rx_bytes[addr]} bytes, {self.rx_packets[addr]} packets")

    async def _run(self):
        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: DatagramProtocol(self.loop, self.recv),
            local_addr=(self._host, self._port),
        )
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
