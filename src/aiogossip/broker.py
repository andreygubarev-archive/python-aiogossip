import asyncio

import typeguard

from .address import Address, to_address


class Broker:
    PACKET_SIZE = 8192

    """A broker is a server that receives and forwards messages to other brokers or clients."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.transport = None

    def transport_set(self, transport):
        """Set the transport for the broker."""
        self.transport = transport

    def transport_unset(self):
        """Unset the transport for the broker."""
        self.transport = None

    @property
    def transport_addr(self):
        return to_address(self.transport.get_extra_info("sockname"))

    @typeguard.typechecked
    def send(self, data: bytes, addr: Address):
        """Send a message to a given address."""
        if len(data) > self.PACKET_SIZE:
            raise ValueError(f"Message size exceeds packet size of {self.PACKET_SIZE} bytes: {len(data)}")

        self.transport.sendto(data, addr.to_tuple())
        print(f"Sent {data} to {addr}")

    @typeguard.typechecked
    def recv(self, data: bytes, addr: Address):
        """Receive a message from an address."""
        addr = to_address(addr)
        print(f"Received {data} from {addr}")
