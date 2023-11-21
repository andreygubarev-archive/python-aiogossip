import math
import random


class Gossip:
    def __init__(self, transport, peers):
        self.transport = transport
        self.peers = peers

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message, peers):
        message["metadata"]["type"] = "gossip"
        message["metadata"]["hops"] = message["metadata"].get("hops", 0) + 1

        selected_peers = int(math.sqrt(len(peers)))
        selected_peers = random.sample(peers, selected_peers)
        for peer in selected_peers:
            await self.send(message, peer)

    async def recv(self):
        while True:
            message, peer = await self.transport.recv()
            message["metadata"]["sender"] = peer

            if message["metadata"].get("type") == "gossip":
                await self.gossip(message, self.peers)
                continue
            else:
                yield message
                continue
