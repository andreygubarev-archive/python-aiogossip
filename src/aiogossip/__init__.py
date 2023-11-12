import asyncio
import json
import os
import random
import socket
import uuid


class Node:
    GOSSIP_INTERVAL = 5

    def __init__(self, seeds, port=50000, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.id = uuid.uuid4()
        self.address = ("0.0.0.0", port)
        self.seeds = seeds

        self.peers = {}

        # Shared socket for sending and receiving
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)
        self.sock.setblocking(False)

    async def listen(self):
        while True:
            data, addr = await self.loop.sock_recvfrom(self.sock, 1024)
            message = json.loads(data.decode())
            await self.handle(addr, message)

    async def gossip(self):
        while True:
            await asyncio.sleep(self.GOSSIP_INTERVAL)
            message = {
                "id": str(self.id),
                "peers": self.peers,
            }

            if self.peers:
                selected_peers = set(self.peers) - {self.id}
                selected_peers = random.sample(
                    sorted(selected_peers), k=len(selected_peers)
                )
                selected_peers = [self.peers[peer] for peer in selected_peers]
                print(f"Selected peers: {selected_peers}")
            else:
                selected_peers = self.seeds

            for peer in selected_peers:
                await self.send(message, peer)

    async def send(self, message, peer):
        await self.loop.sock_sendto(self.sock, json.dumps(message).encode(), peer)

    async def handle(self, addr, message):
        self.peers[message["node"]] = addr
        for peer in message["peers"]:
            self.peers[peer] = tuple(message["peers"][peer])


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

    node = Node(seeds, port=port)
    listen_task = asyncio.create_task(node.listen())
    gossip_task = asyncio.create_task(node.gossip())

    await asyncio.gather(listen_task, gossip_task)


if __name__ == "__main__":
    asyncio.run(main())
