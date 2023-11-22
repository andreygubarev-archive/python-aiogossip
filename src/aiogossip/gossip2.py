import math
import random
import uuid

from .mutex import mutex


class Gossip:
    FANOUT = 5

    def __init__(self, transport, peers, fanout=FANOUT):
        self.transport = transport
        self.peers = peers
        self.fanout = fanout
        self._gossip = set()

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message):
        if "gossip" in message["metadata"]:
            gossip_id = message["metadata"]["gossip"]
        else:
            gossip_id = message["metadata"]["gossip"] = uuid.uuid4().hex

        @mutex(gossip_id)
        async def multicast():
            fanout = min(self.fanout, len(self.peers))
            cycles = math.ceil(math.log(len(self.peers), fanout)) if fanout > 0 else 0
            for _ in range(cycles):
                fanout_peers = random.sample(self.peers, fanout)
                for fanout_peer in fanout_peers:
                    await self.send(message, fanout_peer)

        await multicast()

    async def recv(self):
        while True:
            message, peer = await self.transport.recv()
            message["metadata"]["sender"] = peer

            if "gossip" in message["metadata"]:
                await self.gossip(message)

            yield message
