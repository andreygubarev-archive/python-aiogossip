import asyncio
import collections
import json
import os
import random
import socket
import uuid


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
    INTERVAL = 5
    PAYLOAD_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.setblocking(False)

    async def recv(self):
        data, addr = await self.loop.sock_recvfrom(self.sock, self.PAYLOAD_SIZE)
        data = json.loads(data.decode())
        return data, addr

    async def send(self, data, addr):
        data = json.dumps(data).encode()
        await self.loop.sock_sendto(self.sock, data, addr)


class Node:
    GOSSIP_INTERVAL = 5
    GOSSIP_MESSAGE_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.transport = Transport(host, port, loop)
        self.channel = Channel()

        self.node_id = uuid.uuid4()
        self.node_peers = {}

    async def connect(self, seed):
        message = {
            "id": str(self.node_id),
            "peers": self.node_peers,
        }
        await self.send(message, seed)

    async def recv(self):
        while True:
            data, addr = await self.transport.recv()
            await self.handle(data, addr)

    async def send(self, message, peer):
        await self.transport.send(message, peer)

    async def broadcast(self):
        while True:
            await asyncio.sleep(self.GOSSIP_INTERVAL)

            peers = set(self.node_peers) - {self.node_id}
            peers = random.sample(sorted(peers), k=len(peers))
            peers = [self.node_peers[p] for p in peers]
            print(f"Selected peers: {peers}")

            for peer in peers:
                await self.ping(peer)

    async def handle(self, message, addr):
        print(f"Received message: {message}")

        if "id" in message:
            self.node_peers[message["id"]] = addr

        if "peers" in message:
            for p in message["peers"]:
                self.node_peers[p] = tuple(message["peers"][p])

        if "kind" not in message:
            return

        if message["kind"] == "ping":
            self.loop.create_task(self.ack(message["metadata"]["message_id"], addr))

        if message["kind"] == "ack":
            await self.channel.send(message["metadata"]["message_id"], message)

    async def ping(self, peer):
        message_id = str(uuid.uuid4())
        message = {
            "kind": "ping",
            "metadata": {
                "message_id": message_id,
                "node_id": str(self.node_id),
            },
        }
        await self.transport.send(message, peer)
        ack = await self.channel.recv(message_id)
        print(f"Received ack: {ack}")

    async def ack(self, message_id, peer):
        message = {
            "kind": "ack",
            "metadata": {
                "message_id": message_id,
                "node_id": str(self.node_id),
            },
        }
        await self.transport.send(message, peer)


async def main():
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    node = Node(port=port)
    recv_task = asyncio.create_task(node.recv())
    broadcast_task = asyncio.create_task(node.broadcast())

    seed = os.getenv("SEED")
    if seed is not None:
        seed = seed.split(":")
        seeds = [(seed[0], int(seed[1]))]
        await node.connect(seeds[0])

    await asyncio.gather(recv_task, broadcast_task)


if __name__ == "__main__":
    asyncio.run(main())
