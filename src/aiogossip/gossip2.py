import math
import random


class Gossip:
    def __init__(self, transport, peers):
        self.transport = transport
        self.peers = peers

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message):
        message["metadata"]["type"] = "gossip"
        message["metadata"]["hops"] = message["metadata"].get("hops", 0) + 1

        if message["metadata"]["hops"] > int(math.sqrt(len(self.peers))):
            return

        selected_peers = int(math.sqrt(len(self.peers)))
        selected_peers = random.sample(self.peers, selected_peers)
        print(self.transport.addr, "selected peers", selected_peers)
        for peer in selected_peers:
            print(
                self.transport.addr,
                "sending gossip to",
                peer,
                message["metadata"]["hops"],
            )
            await self.send(message, peer)

    async def recv(self):
        while True:
            message, peer = await self.transport.recv()
            message["metadata"]["sender"] = peer

            if message["metadata"].get("type") == "gossip":
                print(
                    self.transport.addr,
                    "received gossip",
                    message["metadata"]["sender"],
                    message["metadata"]["hops"],
                )
                await self.gossip(message)

            yield message
