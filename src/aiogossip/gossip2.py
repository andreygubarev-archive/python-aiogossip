import asyncio
import math
import uuid

from .mutex import mutex
from .topology import Topology


class Gossip:
    FANOUT = 5
    INTERVAL = 0.01  # 10ms

    def __init__(self, transport, topology=None, fanout=FANOUT, interval=INTERVAL):
        self.transport = transport
        self.topology = topology or Topology()
        self._fanout = fanout
        self._interval = interval

    @property
    def fanout(self):
        return min(self._fanout, len(self.topology))

    @property
    def fanout_cycles(self):
        if self.fanout == 0:
            return 0

        if self.fanout == 1:
            return 1

        return math.ceil(math.log(len(self.topology), self.fanout))

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def gossip(self, message):
        if "gossip" in message["metadata"]:
            gossip_id = message["metadata"]["gossip"]
        else:
            gossip_id = message["metadata"]["gossip"] = uuid.uuid4().hex

        @mutex(gossip_id, owner=self.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.fanout_cycles:
                fanout_peers = self.topology.get(sample=self.fanout)
                for fanout_peer in fanout_peers:
                    await self.send(message, fanout_peer)
                cycle += 1
                await asyncio.sleep(self._interval)

        await multicast()

    async def recv(self):
        while True:
            message, peer = await self.transport.recv()
            message["metadata"]["sender"] = peer

            if "gossip" in message["metadata"]:
                await self.gossip(message)

            yield message
