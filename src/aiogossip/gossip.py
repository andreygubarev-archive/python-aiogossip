import asyncio
import collections
import json
import uuid

from . import channel, transport


class GossipOperation:
    PING = 1
    ACK = 2
    QUERY = 3
    RESPOND = 4
    JOIN = 5

    def __init__(self, gossip):
        self.gossip = gossip

    async def ack(self, addr, topic):
        await self.gossip.send(self.ACK, {}, addr, topic=topic)
        return topic

    async def ping(self, addr):
        topic = str(uuid.uuid4())
        recv = self.gossip.loop.create_task(self.gossip.channels[topic].recv())
        await self.gossip.send(self.PING, {}, addr, topic=topic)
        await recv
        await self.gossip.channels[topic].close()
        return topic

    async def query(self, data, addr=None):
        topic = str(uuid.uuid4())

        if addr:
            fanout = [addr]
        else:
            fanout = self.gossip.node_peers.values()

        for addr in fanout:
            await self.gossip.send(self.QUERY, data, addr, topic=topic)

        r = []
        while len(r) < len(fanout):
            message = await self.gossip.channels[topic].recv()
            if message["metadata"]["message_type"] == self.RESPOND:
                r.append(message)

        await self.gossip.channels[topic].close()

        print("Query result:", json.dumps(r, indent=2))
        return r

    async def respond(self, addr, topic, data):
        await self.gossip.send(self.RESPOND, data, addr, topic=topic)

    async def join(self, data):
        fanout = self.gossip.node_peers.values()
        for addr in fanout:
            await self.gossip.send(self.JOIN, data, addr)


class Gossip:
    TRANSPORT = transport.Transport
    INTERVAL = 1
    TIMEOUT = 5

    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.transport = self.TRANSPORT((host, port), loop=self.loop)

        self.node_id = uuid.uuid4()
        self.node_peers = {}
        self.channels = collections.defaultdict(channel.Channel)

        self.tasks = []
        self.tasks.append(self.loop.create_task(self._recv()))
        self.tasks.append(self.loop.create_task(self._ping()))

        self.op = GossipOperation(self)

    async def _recv(self):
        while True:
            message, addr = await self.transport.recv()
            message["metadata"]["sender_addr"] = addr

            metadata = message["metadata"]
            if metadata["sender_id"] not in self.node_peers:
                self.node_peers[metadata["sender_id"]] = metadata["sender_addr"]
                await self.op.join(
                    {
                        "node_id": metadata["sender_id"],
                        "node_addr": metadata["sender_addr"],
                    }
                )

            await self.channels["recv"].send(message)

    async def _ping(self):
        # Round-Robin Probe Target Selection
        # https://en.wikipedia.org/wiki/SWIM_Protocol#Extensions
        while True:
            if not self.node_peers:
                await asyncio.sleep(self.INTERVAL)
                continue

            peer_ids = list(self.node_peers.keys())
            for peer_id in peer_ids:
                await asyncio.sleep(self.INTERVAL)
                addr = self.node_peers[peer_id]
                await self.op.ping(addr)

    async def recv(self):
        while True:
            message = await self.channels["recv"].recv()
            # print(f"Received message: {message}")
            metadata, data = message["metadata"], message["data"]

            if metadata.get("sender_topic") in self.channels:
                await self.channels[metadata["sender_topic"]].send(message)

            message_type = metadata["message_type"]
            if message_type == GossipOperation.PING:
                await self.op.ack(
                    metadata["sender_addr"],
                    topic=metadata["sender_topic"],
                )
                continue
            elif message_type == GossipOperation.ACK:
                continue
            elif message_type == GossipOperation.JOIN:
                self.node_peers[data["node_id"]] = tuple(data["node_addr"])
                continue

            yield message

    async def send(self, message_type, data, addr, topic=None):
        data = {
            "metadata": {
                "sender_id": str(self.node_id),
                "sender_topic": topic,
                "message_id": str(uuid.uuid4()),
                "message_type": message_type,
            },
            "data": data,
        }
        await self.transport.send(data, addr)
