import asyncio

from .address import to_address


class GossipProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, on_message):
        self.loop = loop
        self.on_message = on_message

        self.transport = None
        self.transport_disconnected = self.loop.create_future()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport_disconnected.set_result(True)

    def datagram_received(self, data, addr):
        self.on_message(data, to_address(addr))

    def error_received(self, exc):
        pass
