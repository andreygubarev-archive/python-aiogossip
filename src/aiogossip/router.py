import asyncio
import collections

from .channel import Channel
from .gossip import Gossip


class Router:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.channels = collections.defaultdict(Channel)
        self.subscriptions = []

    async def listen(self):
        async for message in self.gossip.recv():
            await self.channels[message["metadata"]["topic"]].send(message)

    async def publish(self, topic, message, nodes=None):
        message["metadata"]["topic"] = topic
        await self.gossip.gossip(message)

    def subscribe(self, topic, callback):
        async def subscription():
            while True:
                message = await self.channels[topic].recv()
                return await callback(message)

        s = self.loop.create_task(subscription())
        self.subscriptions.append(s)
