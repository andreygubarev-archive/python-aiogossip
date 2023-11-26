import math
import uuid

from .mutex import mutex
from .topology import Node, Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, topology=None, fanout=None, identity=None):
        self.identity = identity or uuid.uuid4().hex
        self.transport = transport

        self.topology = topology or Topology()
        self.topology.node = Node(self.identity, self.transport.addr)

        self._fanout = fanout or self.FANOUT

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
        if "route" not in message["metadata"]:
            message["metadata"]["route"] = []
        message["metadata"]["route"].append(self.topology.route)
        await self.transport.send(message, node.address.addr)

    async def gossip(self, message):
        if "gossip_id" in message["metadata"]:
            gossip_id = message["metadata"]["gossip_id"]
        else:
            gossip_id = message["metadata"]["gossip_id"] = uuid.uuid4().hex

        fanout_ignore = [self.identity]
        if "route" in message["metadata"]:
            fanout_ignore.extend([r[0] for r in message["metadata"]["route"]])

        @mutex(gossip_id, owner=self.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.fanout_cycles:
                fanout_nodes = self.topology.sample(self.fanout, ignore=fanout_ignore)
                for node in fanout_nodes:
                    await self.send(message, node)
                cycle += 1
                fanout_ignore.extend([n.identity for n in fanout_nodes])

        await multicast()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["route"][-1].append(addr)

            nodes = [Node(r[0], r[-1]) for r in message["metadata"]["route"]]
            self.topology.add(nodes)  # establish bidirectional connection

            if "gossip_id" in message["metadata"]:
                await self.gossip(message)

            yield message

    async def close(self):
        self.transport.close()
