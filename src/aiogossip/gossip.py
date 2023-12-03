import math
import uuid

from .message_pb2 import Message
from .mutex import mutex
from .topology import Topology


class Gossip:
    FANOUT = 5

    def __init__(self, transport, fanout=None, peer_id=None):
        self.peer_id = peer_id or uuid.uuid4().bytes
        self.transport = transport
        self.topology = Topology(self.peer_id, self.transport.addr)

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

    async def send(self, message, peer_id):
        msg = Message()
        msg.CopyFrom(message)

        if peer_id == self.peer_id:
            raise ValueError("cannot send message to self:", msg)

        if not msg.message_type:
            raise ValueError("message type is required:", msg)

        if not msg.message_id:
            msg.message_id = uuid.uuid4().bytes

        if not msg.metadata.src:
            msg.metadata.src = self.peer_id

        msg.metadata.dst = peer_id
        self.topology.append_route(msg)

        addr = self.topology.get_addr(peer_id)
        await self.transport.send(msg, addr)

    async def send_ack(self, message):
        msg = Message()
        msg.CopyFrom(message)

        msg.ClearField("message_id")
        msg.metadata.ClearField("src")

        if msg.metadata.ack:
            return False

        msg.metadata.ack = self.peer_id
        await self.send(msg, msg.metadata.syn)
        return True

    async def send_forward(self, message):
        msg = Message()
        msg.CopyFrom(message)

        if msg.metadata.dst == self.peer_id:
            return False
        else:
            await self.send(msg, msg.metadata.dst)
            return True

    async def send_gossip(self, message):
        msg = Message()
        msg.CopyFrom(message)

        msg.ClearField("message_id")
        msg.metadata.ClearField("src")

        if not msg.metadata.gossip:
            msg.metadata.gossip = uuid.uuid4().bytes

        gossip_ignore = set([self.peer_id])
        gossip_ignore.update([r.route_id for r in msg.metadata.route])

        @mutex(self, msg.metadata.gossip)
        async def multicast():
            cycle = 0
            while cycle < self.cycles:
                peer_ids = self.topology.sample(self.fanout, ignore=gossip_ignore)
                for peer_id in peer_ids:
                    await self.send(msg, peer_id)
                gossip_ignore.update(peer_ids)
                cycle += 1

        await multicast()

    async def recv(self):
        while True:
            msg, addr = await self.transport.recv()
            msg.metadata.route[-1].daddr = f"{addr[0]}:{addr[1]}"

            peer_ids = self.topology.update_route(msg)
            for peer_id in peer_ids:
                await self.send(Message(), peer_id)
            self.topology.append_route(msg)

            # forward message to destination
            if await self.send_forward(msg):
                continue

            # gossip message
            if msg.metadata.gossip:
                await self.send_gossip(msg)

            # acknowledge message
            if msg.metadata.syn:
                await self.send_ack(msg)

            yield msg

    async def close(self):
        self.transport.close()
