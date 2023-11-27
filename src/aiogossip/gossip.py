import copy
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
        message = copy.deepcopy(message)

        route = message["metadata"].get("route", [self.topology.route])
        if route[-1][0] != self.identity:
            route.append(self.topology.route)
        message["metadata"]["route"] = route

        await self.transport.send(message, node.address.addr)

    async def gossip(self, message):
        gossip_id = message["metadata"]["gossip"] = message["metadata"].get(
            "gossip", uuid.uuid4().hex
        )

        fanout_ignore = set([self.identity])
        fanout_ignore.update([r[0] for r in message["metadata"].get("route", [])])

        @mutex(gossip_id, owner=self.gossip)
        async def fanout():
            cycle = 0
            while cycle < self.fanout_cycles:
                fanout_nodes = self.topology.sample(self.fanout, ignore=fanout_ignore)
                for fanout_node in fanout_nodes:
                    await self.send(message, fanout_node)
                fanout_ignore.update([n.identity for n in fanout_nodes])
                cycle += 1

        await fanout()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["route"][-1].append(list(addr))

            nodes = [Node(r[0], r[-1]) for r in message["metadata"]["route"]]
            self.topology.add(nodes)  # establish bidirectional connection

            if "gossip" in message["metadata"]:
                await self.gossip(message)

            yield message

    async def close(self):
        self.transport.close()
