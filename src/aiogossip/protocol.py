import asyncio

from .address import to_address
from .message import to_message


class DatagramProtocol(asyncio.DatagramProtocol):
    """A simple datagram protocol that calls a callback when a message is received."""

    def __init__(self, loop, recv):
        """Initialize the protocol with a loop and a callback."""
        self.loop = loop
        self.recv = recv

        self.transport = None
        self.transport_closed = self.loop.create_future()

    def connection_made(self, transport):
        """Called when a connection is made."""
        self.transport = transport

    def connection_lost(self, exc):
        """Called when a connection is lost."""
        self.transport_closed.set_result(True)

    def datagram_received(self, data, addr):
        """Called when a datagram is received."""
        msg = to_message(data)
        addr = to_address(addr)
        self.recv(msg, addr)

    def error_received(self, exc):
        """Called when an error is received."""
        pass
