import asyncio
import collections
import itertools

from .channel import Channel
from .gossip import Gossip


class Callback:
    def __init__(self, func, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.func = func
        self.chan = Channel()

        self.task = self.loop.create_task(self())

    async def __call__(self):
        while True:
            try:
                message = await self.chan.recv()
                await self.func(message)
            except asyncio.CancelledError:
                break

    async def cancel(self):
        self.task.cancel()
        await self.task


class Broker:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.callbacks = collections.defaultdict(list)

    async def connect(self):
        """Connect to the gossip network and start receiving messages."""
        async for message in self.gossip.recv():
            # FIXME: handle messages with no topic
            for callback in self.callbacks[message["metadata"]["topic"]]:
                await callback.chan.send(message)

    async def disconnect(self):
        """Disconnect from the gossip network and stop receiving messages."""
        callbacks = [cb for cb in itertools.chain(*self.callbacks.values())]
        await asyncio.gather(*[cb.cancel() for cb in callbacks], return_exceptions=True)
        await self.gossip.close()

    def subscribe(self, topic, func):
        callback = Callback(func, loop=self.loop)
        self.callbacks[topic].append(callback)
        return callback

    async def unsubscribe(self, topic, callback):
        await callback.cancel()
        self.callbacks[topic].remove(callback)

    async def publish(self, topic, message, nodes=None):
        message["metadata"]["topic"] = topic
        await self.gossip.gossip(message)
