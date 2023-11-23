import asyncio
import collections
import itertools

from .channel import Channel
from .gossip import Gossip


class Router:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.chan = collections.defaultdict(Channel)
        self.subs = collections.defaultdict(list)

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

        task = self.loop.create_task(sub())
        self.subs[topic].append(task)

    async def close(self):
        for tasks in self.subs.values():
            for task in tasks:
                task.cancel()
        await asyncio.gather(
            *itertools.chain(*self.subs.values()), return_exceptions=True
        )
        await self.gossip.close()
