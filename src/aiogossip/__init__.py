import asyncio
import collections
import json
import os
import socket
import uuid


class MESSAGE:
    PING = 1
    ACK = 2


class Channel:
    TIMEOUT = 10

    def __init__(self):
        self._channel = collections.defaultdict(asyncio.Queue)

    async def send(self, key, value):
        chan = self._channel[key]
        await chan.put(value)

    async def recv(self, key, timeout=TIMEOUT):
        chan = self._channel[key]
        async with asyncio.timeout(timeout):
            r = await chan.get()
            chan.task_done()
            return r

    async def close(self, key):
        chan = self._channel[key]
        async with asyncio.timeout(self.TIMEOUT):
            await chan.join()
        self._channel.pop(key, None)


class Transport:
    PAYLOAD_SIZE = 4096

    def __init__(self, bind, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(bind)
        self.sock.setblocking(False)

    async def recv(self):
        data, addr = await self.loop.sock_recvfrom(self.sock, self.PAYLOAD_SIZE)
        data = json.loads(data.decode())
        return data, addr

    async def send(self, data, addr):
        data = json.dumps(data).encode()
        await self.loop.sock_sendto(self.sock, data, addr)


class Gossip:
    TRANSPORT = Transport
    INTERVAL = 1
    TIMEOUT = 5

    def __init__(self, bind, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.transport = self.TRANSPORT(bind, loop=self.loop)

        self.node_id = uuid.uuid4()
        self.node_peers = {}
        self.channel = Channel()

        self.failure_detector = self.loop.create_task(self.failure_detect())

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
                await self.ping_recv(topic)

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
                await self.ack_send(data["topic"], metadata["sender_addr"])
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

    async def ack_send(self, topic, addr):
        await self.send(MESSAGE.ACK, {"topic": topic}, addr)
        return topic

    async def ack_recv(self, topic):
        await self.channel.send(topic, {})

    async def ping_send(self, addr):
        topic = str(uuid.uuid4())
        await self.send(MESSAGE.PING, {"topic": topic}, addr)
        return topic

    async def ping_recv(self, topic):
        async with asyncio.timeout(self.TIMEOUT):
            await self.channel.recv(topic)
        await self.channel.close(topic)


class Node:
    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.gossip = Gossip((host, port), loop=self.loop)
        self.channel = Channel()

    async def recv(self):
        async for payload, addr in self.gossip.listen():
            await self.handle(payload, addr)

    async def send(self, message, peer):
        await self.gossip.send(message, peer)

    async def handle(self, message, addr):
        print(f"Received message: {message}")

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
