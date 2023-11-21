import math
import random


class Gossip:
    def __init__(self, transport):
        self.transport = transport

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message, peers):
        selected_peers = int(math.sqrt(len(peers))) or 1
        selected_peers = random.sample(peers, selected_peers)
        for peer in selected_peers:
            await self.send(message, peer)

    async def recv(self):
        while True:
            message, peer = await self.transport.recv()
            # message["metadata"]["sender"] = peer
            yield message
