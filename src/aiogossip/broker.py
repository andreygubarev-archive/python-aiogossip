import asyncio

import typeguard

from .address import Address, to_address
from .message import Message
from .topology import Topology


class Broker:
    """A broker is a server that receives and forwards messages to other brokers or clients."""

    PACKET_SIZE = 8192

    def __init__(self, loop: asyncio.AbstractEventLoop, topology: Topology, dispatch: callable):
        self.loop = loop
        self.topology = topology
        self._dispatch = dispatch

        self._transport = None

    @property
    def transport(self):
        return self._transport

    @transport.setter
    def transport(self, transport):
        self._transport = transport

    @transport.deleter
    def transport(self):
        if self._transport:
            self._transport.close()
        self._transport = None

    @property
    def addr(self):
        return to_address(self.transport.get_extra_info("sockname"))

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        """Send a message to a given address."""
        if len(data) > self.PACKET_SIZE:
            raise ValueError(f"Message size exceeds packet size of {self.PACKET_SIZE} bytes: {len(data)}")

        print(f"Sent {data} to {addr}")
        self.transport.sendto(data, addr.to_tuple())

    @typeguard.typechecked
    def recv(self, msg: Message, addr: Address):
        """Receive a message from an address."""
        print(f"Received {msg} from {addr}")

        self.topology.add_node(addr)
        self._dispatch(msg, addr)

    def close(self):
        """Close the broker."""
        del self.transport
