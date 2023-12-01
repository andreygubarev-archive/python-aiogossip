import math
import uuid

from .message_pb2 import Message
from .mutex import mutex
from .topology import Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, fanout=None, node_id=None):
        self.node_id = node_id or uuid.uuid4().bytes
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

    async def send(self, _message, node_id):
        message = Message()
        message.CopyFrom(_message)

        if node_id == self.node_id:
            raise ValueError("cannot send message to self")

        if not message.message_id:
            message.message_id = uuid.uuid4().bytes
        if not message.metadata.src:
            message.metadata.src = self.node_id
        message.metadata.dst = node_id
        self.topology.set_route(message)

        addr = self.topology.get_addr(node_id)
        await self.transport.send(message, addr)

    async def send_ack(self, _message):
        message = Message()
        message.CopyFrom(_message)

        if message.metadata.ack:
            return False

        message.ClearField("message_id")
        message.metadata.ClearField("src")

        message.metadata.ack = self.node_id
        await self.send(message, message.metadata.syn)
        return True

    async def send_forward(self, _message):
        message = Message()
        message.CopyFrom(_message)

        if message.metadata.dst == self.node_id:
            return False
        else:
            await self.send(message, message.metadata.dst)
            return True

    async def send_gossip(self, _message):
        message = Message()
        message.CopyFrom(_message)
        message.ClearField("message_id")
        message.metadata.ClearField("src")

        if not message.metadata.gossip:
            message.metadata.gossip = uuid.uuid4().bytes

        gossip_ignore = set([self.node_id])
        gossip_ignore.update([r.route_id for r in message.metadata.route])

        @mutex(message.metadata.gossip, owner=self.send_gossip)
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
            message.metadata.route[-1].daddr = f"{addr[0]}:{addr[1]}"

            self.topology.set_route(message)
            node_ids = self.topology.update_routes(message)

            # connect to new nodes
            for node_id in node_ids:
                await self.send(Message(), node_id)

            # forward message to destination
            if await self.send_forward(message):
                continue

            # gossip message
            if message.metadata.gossip:
                await self.send_gossip(message)

            # acknowledge message
            if message.metadata.syn:
                await self.send_ack(message)

            yield message

    async def close(self):
        self.transport.close()
