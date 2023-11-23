import asyncio
import collections

from .channel import Channel
from .gossip import Gossip


class Router:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.chan = collections.defaultdict(Channel)
        self.subs = []

    async def listen(self):
        async for message in self.gossip.recv():
            await self.chan[message["metadata"]["topic"]].send(message)

    async def publish(self, topic, message, nodes=None):
        message["metadata"]["topic"] = topic
        await self.gossip.gossip(message)

    def subscribe(self, topic, callback):
        async def sub():
            while True:
                try:
                    message = await self.chan[topic].recv()
                    await callback(message)
                except asyncio.CancelledError:
                    break

        sub = self.loop.create_task(sub())
        self.subs.append(sub)

    async def close(self):
        for sub in self.subs:
            sub.cancel()
        await asyncio.gather(*self.subs, return_exceptions=True)
        await self.gossip.close()
