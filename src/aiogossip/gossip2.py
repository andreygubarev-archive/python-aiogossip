import math
import random


class Gossip:
    FANOUT = 3

    def __init__(self, transport, peers, fanout=FANOUT):
        self.transport = transport
        self.peers = peers
        self.fanout = fanout

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message):
        message["metadata"]["type"] = "gossip"
        message["metadata"]["time-to-live"] = message["metadata"].get(
            "time-to-live", math.ceil(math.log(len(self.peers), self.fanout))
        )

        if message["metadata"]["time-to-live"] == 0:
            return
        else:
            message["metadata"]["time-to-live"] -= 1

        fanout_peers = random.sample(self.peers, min(self.fanout, len(self.peers)))
        print(self.transport.addr, "fanout peers", fanout_peers)
        for peer in fanout_peers:
            print(
                self.transport.addr,
                "sending gossip to",
                peer,
                message["metadata"]["time-to-live"],
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
                    message["metadata"]["time-to-live"],
                )
                await self.gossip(message)

            yield message
