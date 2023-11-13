import asyncio
import os
import uuid

from . import channel, transport


class MESSAGE:
    PING = 1
    ACK = 2


class Gossip:
    TRANSPORT = transport.Transport
    INTERVAL = 1
    TIMEOUT = 5

    def __init__(self, bind, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.transport = self.TRANSPORT(bind, loop=self.loop)

        self.node_id = uuid.uuid4()
        self.node_peers = {}
        self.channel = channel.Channel()

        self.failure_detector = self.loop.create_task(self.failure_detect())

    async def listen(self):
        while True:
            data, addr = await self.transport.recv()
            metadata, data = data["metadata"], data["data"]
            metadata["sender_addr"] = addr
            print(f"Received message: {metadata} {data}")

            if metadata["sender_id"] not in self.node_peers:
                self.node_peers[metadata["sender_id"]] = metadata["sender_addr"]

            # message_id = metadata["message_id"]
            message_type = metadata["message_type"]

            if message_type == MESSAGE.PING:
                await self.ping_recv(data["topic"], metadata["sender_addr"])
                continue
            elif message_type == MESSAGE.ACK:
                await self.ack_recv(data["topic"])
                continue
            else:
                # TODO: Handle unknown message type
                yield metadata, data

    async def send(self, message_type, data, addr):
        data = {
            "metadata": {
                "sender_id": str(self.node_id),
                "message_id": str(uuid.uuid4()),
                "message_type": message_type,
            },
            "data": data,
        }
        await self.transport.send(data, addr)

    async def failure_detect(self):
        # Round-Robin Probe Target Selection
        # https://en.wikipedia.org/wiki/SWIM_Protocol#Extensions
        while True:
            if not self.node_peers:
                await asyncio.sleep(self.INTERVAL)

            for peer_id in self.node_peers:
                await asyncio.sleep(self.INTERVAL)
                addr = self.node_peers[peer_id]

                topic = await self.ping_send(addr)
                await self.ping_wait(topic)

    async def ack_send(self, topic, addr):
        await self.send(MESSAGE.ACK, {"topic": topic}, addr)
        return topic

    async def ack_recv(self, topic):
        await self.channel.send(topic, {})

    async def ping_send(self, addr):
        topic = str(uuid.uuid4())
        await self.send(MESSAGE.PING, {"topic": topic}, addr)
        return topic

    async def ping_wait(self, topic):
        async with asyncio.timeout(self.TIMEOUT):
            await self.channel.recv(topic)
        await self.channel.close(topic)

    async def ping_recv(self, topic, addr):
        await self.ack_send(topic, addr)


class Node:
    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.gossip = Gossip((host, port), loop=self.loop)
        self.channel = channel.Channel()

    async def recv(self):
        async for payload, addr in self.gossip.listen():
            await self.handle(payload, addr)

    async def send(self, message, peer):
        await self.gossip.send(message, peer)

    async def handle(self, message, addr):
        print(f"Handle message: {message}")
        if "kind" not in message:
            return


async def main():
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    node = Node(port=port)
    recv_task = asyncio.create_task(node.recv())

    seed = os.getenv("SEED")
    if seed is not None:
        seed = seed.split(":")
        seed = (seed[0], int(seed[1]))
        await node.gossip.ping_send(seed)

    await asyncio.gather(recv_task, node.gossip.failure_detector)


if __name__ == "__main__":
    asyncio.run(main())
