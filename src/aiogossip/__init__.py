import asyncio
import json
import os
import random
import socket
import time


class ServerNode:
    def __init__(self, peers, port=50000):
        self.address = ("0.0.0.0", port)
        self.peers = peers
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
                "type": "gossip",
                "timestamp": self.configuration["timestamp"],
                "data": self.configuration["data"],
            }
            selected_peers = random.sample(self.peers, k=len(self.peers))
            for peer in selected_peers:
                await self.send_message(message, peer)

    async def send_message(self, message, peer):
        loop = asyncio.get_running_loop()
        await loop.sock_sendto(self.sock, json.dumps(message).encode(), peer)

    async def handle_incoming_message(self, addr, message):
        if addr not in self.peers:
            self.peers.append(addr)

        if message["timestamp"] > self.configuration["timestamp"]:
            self.configuration.update(message)


async def main():
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    peer = os.getenv("PEER")
    if peer is None:
        peers = []
    else:
        peer = peer.split(":")
        peers = [(peer[0], int(peer[1]))]

    node = ServerNode(peers, port=port)
    listen_task = asyncio.create_task(node.listen())
    gossip_task = asyncio.create_task(node.gossip())

    await asyncio.gather(listen_task, gossip_task)


if __name__ == "__main__":
    asyncio.run(main())
