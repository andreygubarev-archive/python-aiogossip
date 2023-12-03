import math
import uuid

from .concurrency.mutex import mutex
from .message_pb2 import Message
from .topology import Topology


class Gossip:
    """
    Gossip class represents a gossip protocol implementation.

    Attributes:
        FANOUT (int): The default fanout value for the gossip protocol.
    """

    FANOUT = 5

    def __init__(self, transport, fanout=None, peer_id=None):
        """
        Initialize a Gossip instance.

        Args:
            transport (Transport): The transport object used for sending and receiving messages.
            fanout (int, optional): The fanout value for the gossip protocol. Defaults to None.
            peer_id (bytes, optional): The ID of the peer. Defaults to None.
        """
        self.peer_id = peer_id or uuid.uuid4().bytes
        self.transport = transport
        self.topology = Topology(self.peer_id, self.transport.addr)

        self._fanout = fanout or self.FANOUT

    async def close(self):
        """
        Close the Gossip instance and the associated transport.
        """
        self.transport.close()

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
        if not message.id:
            raise ValueError("message id is required:", message)

        if not message.kind:
            raise ValueError("message kind is required:", message)

        if not message.routing.src_id:
            raise ValueError("message routing.src_id is required:", message)

        if not message.routing.dst_id:
            raise ValueError("message routing.dst_id is required:", message)

        msg = Message()
        msg.CopyFrom(message)
        msg = self.topology.append_route(msg)

        addr = self.topology.get_addr(peer_id)
        await self.transport.send(msg, addr)
        return msg.id

    async def send_handshake(self, peer_id):
        msg = Message()
        msg.id = uuid.uuid4().bytes
        msg.kind.append(Message.Kind.HANDSHAKE)
        msg.kind.append(Message.Kind.SYN)
        msg.routing.src_id = self.peer_id
        msg.routing.dst_id = peer_id

        return await self.send(msg, peer_id)

    async def send_forward(self, message):
        msg = Message()
        msg.CopyFrom(message)

        return await self.send(msg, message.routing.dst_id)

    async def send_ack(self, message):
        if message.Kind.SYN not in message.kind:
            raise ValueError("SYN message is required for ACK:", message)

        msg = Message()
        msg.id = message.id
        msg.kind.append(Message.Kind.ACK)
        msg.routing.src_id = self.peer_id
        msg.routing.dst_id = message.routing.src_id
        msg.topic = message.topic

        return await self.send(msg, message.routing.src_id)

    async def send_gossip(self, message):
        msg = Message()
        msg.CopyFrom(message)

        if not msg.id:
            msg.id = uuid.uuid4().bytes

        if Message.Kind.GOSSIP not in msg.kind:
            msg.kind.append(Message.Kind.GOSSIP)

        if not msg.routing.src_id:
            msg.routing.src_id = self.peer_id

        messages = set()
        gossip_ignore = set([self.peer_id])
        gossip_ignore.update([r.route_id for r in msg.routing.routes])

        @mutex(self, msg.id)
        async def multicast():
            cycle = 0
            while cycle < self.cycles:
                peer_ids = self.topology.sample(self.fanout, ignore=gossip_ignore)
                for peer_id in peer_ids:
                    m = Message()
                    m.CopyFrom(msg)
                    m.routing.dst_id = peer_id
                    messages.add(await self.send(m, peer_id))
                gossip_ignore.update(peer_ids)
                cycle += 1

        await multicast()
        return list(messages)

    async def send_gossip_handshake(self):
        msg = Message()
        msg.id = uuid.uuid4().bytes
        msg.kind.append(Message.Kind.HANDSHAKE)
        msg.kind.append(Message.Kind.SYN)
        msg.routing.src_id = self.peer_id

        return await self.send_gossip(msg)

    async def recv(self):
        while True:
            msg, addr = await self.transport.recv()
            msg.routing.routes[-1].daddr = f"{addr[0]}:{addr[1]}"

            msg = self.topology.append_route(msg)
            route_ids = self.topology.update(msg.routing.routes)
            for route_id in route_ids:
                await self.send_handshake(route_id)

            # forward message to destination
            if self.peer_id != msg.routing.dst_id:
                await self.send_forward(msg)
                continue

            # ack message
            if Message.Kind.ACK in msg.kind:
                yield msg
                continue

            # syn message
            if Message.Kind.SYN in msg.kind:
                await self.send_ack(msg)

            # gossip message
            if Message.Kind.GOSSIP in msg.kind:
                await self.send_gossip(msg)

            # handshake message
            if Message.Kind.HANDSHAKE in msg.kind:
                continue

            yield msg
