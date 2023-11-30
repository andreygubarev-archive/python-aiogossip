import math
import uuid

from .mutex import mutex
from .topology import Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, fanout=None, node_id=None):
        self.node_id = node_id or uuid.uuid4().hex
        self.transport = transport

        self.topology = Topology(self.node_id, self.transport.addr)

        self._fanout = fanout or self.FANOUT

    @property
    def fanout(self):
        return min(self._fanout, len(self.topology))

    @property
    def cycles(self):
        if self.fanout == 0:
            return 0

        if self.fanout == 1:
            return 1

        return math.ceil(math.log(len(self.topology), self.fanout))

    async def send(self, message, node_id):
        if node_id == self.node_id:
            raise ValueError("cannot send message to self")

        message["metadata"].setdefault("event", uuid.uuid4().hex)
        message["metadata"].setdefault("src", self.node_id)
        message["metadata"]["dst"] = node_id
        self.topology.set_route(message)

        addr = self.topology.get_addr(node_id)
        await self.transport.send(message, addr)

    async def gossip(self, message):
        gossip_id = message["metadata"].setdefault("gossip", uuid.uuid4().hex)
        gossip_ignore = set([self.node_id])
        gossip_ignore.update([r[1] for r in message["metadata"].get("route", [])])

        @mutex(gossip_id, owner=self.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.cycles:
                node_ids = self.topology.sample(self.fanout, ignore=gossip_ignore)
                for node_id in node_ids:
                    await self.send(message, node_id)
                gossip_ignore.update(node_ids)
                cycle += 1

        await multicast()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["route"][-1].append(list(addr))

            self.topology.set_route(message)
            node_ids = self.topology.update_routes(message["metadata"]["route"])

            # connect to new nodes
            for node_id in node_ids:
                await self.send({"metadata": {}}, node_id)

            # forward message to destination
            if message["metadata"]["dst"] != self.node_id:
                await self.send(message, message["metadata"]["dst"])
                continue

            # acknowledge message
            if "syn" in message["metadata"]:
                if "ack" in message["metadata"]:
                    pass
                else:
                    message["metadata"]["ack"] = self.node_id
                    del message["metadata"]["event"]
                    del message["metadata"]["src"]
                    await self.send(message, message["metadata"]["syn"])

            # gossip message
            if "gossip" in message["metadata"]:
                del message["metadata"]["event"]
                del message["metadata"]["src"]
                await self.gossip(message)

            yield message

    async def close(self):
        self.transport.close()
