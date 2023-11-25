import math
import uuid

from .mutex import mutex
from .topology import Node, Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, topology=None, fanout=FANOUT, identity=None):
        self.identity = identity or uuid.uuid4().hex
        self.transport = transport

        self.topology = topology or Topology()
        self.topology.node = Node(self.identity, self.transport.addr)

        self._fanout = fanout

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
        message["metadata"]["sender_id"] = self.identity
        await self.transport.send(message, node.address.addr)

    async def gossip(self, message):
        if "gossip_id" in message["metadata"]:
            gossip_id = message["metadata"]["gossip_id"]
            gossip_sender_id = message["metadata"]["gossip_sender_id"]
        else:
            gossip_id = message["metadata"]["gossip_id"] = uuid.uuid4().hex
            gossip_sender_id = message["metadata"]["gossip_sender_id"] = self.identity

        fanout_excludes = [self.identity, gossip_sender_id]
        if "sender_id" in message["metadata"]:
            fanout_excludes.append(message["metadata"]["sender_id"])

        @mutex(gossip_id, owner=self.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.fanout_cycles:
                fanout_nodes = self.topology.get(
                    sample=self.fanout,
                    exclude=fanout_excludes,
                )
                for node in fanout_nodes:
                    await self.send(message, node)
                cycle += 1
                fanout_excludes.extend([n.identity for n in fanout_nodes])

        await multicast()

    async def recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["sender_addr"] = addr
            sender_node = Node(message["metadata"]["sender_id"], addr)
            self.topology.add([sender_node])  # establish bidirectional connection

            if "gossip_id" in message["metadata"]:
                await self.gossip(message)

            yield message

    async def close(self):
        self.transport.close()
