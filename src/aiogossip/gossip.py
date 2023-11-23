import asyncio
import math
import uuid

from .mutex import mutex
from .topology import Node, Topology


class Gossip:
    FANOUT = 5
    INTERVAL = 0.01  # 10ms

    def __init__(
        self, transport, topology=None, fanout=FANOUT, interval=INTERVAL, identity=None
    ):
        self.identity = identity or uuid.uuid4().hex
        self.transport = transport

        self.topology = topology or Topology()
        self.topology.node = Node(self.identity, self.transport.addr)

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

    async def send(self, message, node):
        message["metadata"]["source_id"] = self.identity
        await self.transport.send(message, node.address.addr)

    async def gossip(self, message):
        if "gossip" in message["metadata"]:
            gossip_id = message["metadata"]["gossip"]
        else:
            gossip_id = message["metadata"]["gossip"] = uuid.uuid4().hex

        @mutex(gossip_id, owner=self.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.fanout_cycles:
                nodes = self.topology.get(sample=self.fanout)
                for node in nodes:
                    await self.send(message, node)
                cycle += 1
                await asyncio.sleep(self._interval)

        await multicast()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            node = Node(message["metadata"]["source_id"], addr)
            self.topology.add([node])  # establish bidirectional connection

            if "gossip" in message["metadata"]:
                await self.gossip(message)

            yield message
