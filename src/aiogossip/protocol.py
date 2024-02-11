import asyncio

from .address import to_address


class DatagramProtocol(asyncio.DatagramProtocol):
    """A simple datagram protocol that calls a callback when a message is received."""

    def __init__(self, loop, on_message):
        """Initialize the protocol with a loop and a callback."""
        self.loop = loop
        self.on_message = on_message

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
        self.on_message(data, to_address(addr))

    def error_received(self, exc):
        """Called when an error is received."""
        pass
