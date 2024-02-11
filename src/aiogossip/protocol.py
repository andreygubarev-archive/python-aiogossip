import asyncio


class GossipProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, on_message, on_error, on_connection_lost):
        self.loop = loop

        self.on_message = on_message
        self.on_error = on_error
        self.on_connection_lost = on_connection_lost

        self.transport = None
        self.transport_disconnected = self.loop.create_future()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport_disconnected.set_result(True)
        self.on_connection_lost(exc)

    def datagram_received(self, data, addr):
        self.on_message(data, addr)

    def error_received(self, exc):
        self.on_error(exc)
