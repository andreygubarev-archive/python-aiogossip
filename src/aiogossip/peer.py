import asyncio
import os

from . import gossip


class Peer(gossip.Gossip):
    async def listen(self):
        async for message in self.recv():
            await self.handle(message)

    async def handle(self, message):
        if message["metadata"]["message_type"] == gossip.GossipOperation.QUERY:
            await self.op.respond(
                message["metadata"]["sender_addr"],
                message["metadata"]["sender_topic"],
                {"bar": "baz"},
            )


async def query(peer, seed):
    await asyncio.sleep(3)
    await peer.op.query({"foo": "bar"})


async def main():
    print("Starting node...")
    port = os.getenv("PORT")
    assert port is not None, "PORT environment variable must be set"
    port = int(port)

    peer = Peer(port=port)
    listen_task = asyncio.create_task(peer.listen())

    seed = os.getenv("SEED")
    if seed is not None:
        seed = seed.split(":")
        seed = (seed[0], int(seed[1]))
        await peer.op.ping(seed)
        asyncio.create_task(query(peer, seed))

    await asyncio.gather(listen_task, *peer.tasks)


if __name__ == "__main__":
    asyncio.run(main())
