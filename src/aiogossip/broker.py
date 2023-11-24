import asyncio
import collections
import itertools

from .channel import Channel
from .gossip import Gossip


class Callback:
    def __init__(self, topic, func, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.topic = topic
        self.func = func
        self.chan = Channel()

        self.task = self.loop.create_task(self())

    async def __call__(self):
        while True:
            message = await self.chan.recv()
            await self.func(message)

    async def cancel(self):
        await self.chan.close()
        self.task.cancel()


class Broker:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.callbacks = collections.defaultdict(list)

    async def connect(self):
        """Connect to the gossip network and start receiving messages."""
        async for message in self.gossip.recv():
            # Ignore messages without a topic
            if "topic" not in message["metadata"]:
                continue

            for callback in self.callbacks[message["metadata"]["topic"]]:
                await callback.chan.send(message)

            # Remove empty topics
            for topic in list(self.callbacks.keys()):
                if len(self.callbacks[topic]) == 0:
                    del self.callbacks[topic]

    async def disconnect(self):
        """Disconnect from the gossip network and stop receiving messages."""
        callbacks = [cb for cb in itertools.chain(*self.callbacks.values())]
        await asyncio.gather(*[cb.cancel() for cb in callbacks], return_exceptions=True)
        await self.gossip.close()

    def subscribe(self, topic, callback):
        callback = Callback(topic, callback, loop=self.loop)
        self.callbacks[topic].append(callback)
        return callback

    async def unsubscribe(self, callback):
        await callback.cancel()
        self.callbacks[callback.topic].remove(callback)

    async def publish(self, topic, message, nodes=None):
        message["metadata"]["topic"] = topic
        await self.gossip.gossip(message)
