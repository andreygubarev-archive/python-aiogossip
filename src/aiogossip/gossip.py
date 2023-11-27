import math
import uuid

from .mutex import mutex
from .topology import Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, fanout=None, identity=None):
        self.identity = identity or uuid.uuid4().hex
        self.transport = transport

        self.topology = Topology(self.identity, self.transport.addr)

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

    async def send(self, message, node_id):
        self.topology.set_route(message)
        addr = self.topology.get_addr(node_id)
        await self.transport.send(message, addr)

    async def gossip(self, message):
        gossip_id = message["metadata"]["gossip"] = message["metadata"].get(
            "gossip", uuid.uuid4().hex
        )

        fanout_ignore = set([self.identity])
        fanout_ignore.update([r[1] for r in message["metadata"].get("route", [])])

        @mutex(gossip_id, owner=self.gossip)
        async def fanout():
            cycle = 0
            while cycle < self.fanout_cycles:
                fanout_nodes = self.topology.sample(self.fanout, ignore=fanout_ignore)
                for fanout_node in fanout_nodes:
                    await self.send(message, fanout_node)
                fanout_ignore.update(fanout_nodes)
                cycle += 1

        await fanout()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["route"][-1].append(list(addr))
            self.topology.set_route(message)
            self.topology.update_routes(message["metadata"]["route"])

            if "gossip" in message["metadata"]:
                await self.gossip(message)

            yield message

    async def close(self):
        self.transport.close()
