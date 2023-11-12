import asyncio
import json
import os
import random
import socket
import time
import uuid


class ServerNode:
    def __init__(self, seeds, port=50000):
        self.node = uuid.uuid4()
        self.address = ("0.0.0.0", port)
        self.seeds = seeds

        self.peers = {}
        self.configuration = {"timestamp": time.time(), "data": {}}
        self.gossip_interval = 5  # seconds

        # Shared socket for sending and receiving
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        self.sock.setblocking(False)

    async def listen(self):
        loop = asyncio.get_running_loop()
        while True:
            data, addr = await loop.sock_recvfrom(self.sock, 1024)
            message = json.loads(data.decode())
            print(f"Received message from {addr}: {message}")
            await self.handle_incoming_message(addr, message)

    async def gossip(self):
        while True:
            await asyncio.sleep(self.gossip_interval)
            message = {
                "node": str(self.node),
                "type": "gossip",
                "timestamp": self.configuration["timestamp"],
                "data": self.configuration["data"],
                "peers": self.peers,
            }

            if self.peers:
                selected_peers = set(self.peers) - {self.node}
                selected_peers = random.sample(
                    sorted(selected_peers), k=len(selected_peers)
                )
                selected_peers = [self.peers[peer] for peer in selected_peers]
                print(f"Selected peers: {selected_peers}")
            else:
                selected_peers = self.seeds

            for peer in selected_peers:
                await self.send_message(message, peer)

    async def send_message(self, message, peer):
        loop = asyncio.get_running_loop()
        await loop.sock_sendto(self.sock, json.dumps(message).encode(), peer)

    async def handle_incoming_message(self, addr, message):
        self.peers[message["node"]] = addr
        for peer in message["peers"]:
            self.peers[peer] = tuple(message["peers"][peer])

        if message["timestamp"] > self.configuration["timestamp"]:
            self.configuration.update(message)


async def main():
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    seed = os.getenv("SEED")
    if seed is None:
        seeds = []
    else:
        seed = seed.split(":")
        seeds = [(seed[0], int(seed[1]))]

    node = ServerNode(seeds, port=port)
    listen_task = asyncio.create_task(node.listen())
    gossip_task = asyncio.create_task(node.gossip())

    await asyncio.gather(listen_task, gossip_task)


if __name__ == "__main__":
    asyncio.run(main())
