import asyncio
import collections
import json
import os
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


class Gossip:
    TRANSPORT = Transport
    INTERVAL = 1
    TIMEOUT = 5

    def __init__(self, host, port, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.transport = self.TRANSPORT(host, port, loop)

        self.node_id = uuid.uuid4()
        self.node_peers = {}
        self.channel = Channel()

    async def listen(self):
        while True:
            data, addr = await self.transport.recv()

            node_id = data["node_id"]
            if node_id not in self.node_peers:
                self.node_peers[node_id] = addr

            payload = data["payload"]

            if "ping" in payload:
                await self.send({"ack": payload["ping"]}, addr)

            if "ack" in payload:
                await self.channel.send(payload["ack"], payload)

            yield (payload, addr)

    async def send(self, payload, addr):
        data = {
            "node_id": str(self.node_id),
            "payload": payload,
        }
        await self.transport.send(data, addr)

    async def send_multicast(self, payload, node_peers=None):
        node_peers = node_peers or self.node_peers
        for peer in self.node_peers:
            addr = self.node_peers[peer]
            await self.send(payload, addr)

    async def detect_failure(self):
        while True:
            if len(self.node_peers) == 0:
                await asyncio.sleep(self.INTERVAL)

            for peer in self.node_peers:
                await asyncio.sleep(self.INTERVAL)
                addr = self.node_peers[peer]

                message_id = str(uuid.uuid4())
                try:
                    await self.send({"ping": message_id}, addr)
                except Exception:
                    print(f"Failed peer: {peer}")

                async with asyncio.timeout(self.TIMEOUT):
                    await self.channel.recv(message_id)


class Node:
    GOSSIP_INTERVAL = 5
    GOSSIP_MESSAGE_SIZE = 4096

    def __init__(self, host="0.0.0.0", port=49152, loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.gossip = Gossip(host, port, loop)
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
        async for payload, addr in self.gossip.listen():
            await self.handle(payload, addr)

    async def send(self, message, peer):
        await self.gossip.send(message, peer)

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
        await self.gossip.send(message, peer)
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
        await self.gossip.send(message, peer)


async def main():
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    node = Node(port=port)
    recv_task = asyncio.create_task(node.recv())
    broadcast_task = asyncio.create_task(node.gossip.detect_failure())

    seed = os.getenv("SEED")
    if seed is not None:
        seed = seed.split(":")
        seeds = [(seed[0], int(seed[1]))]
        await node.connect(seeds[0])

    await asyncio.gather(recv_task, broadcast_task)


if __name__ == "__main__":
    asyncio.run(main())
