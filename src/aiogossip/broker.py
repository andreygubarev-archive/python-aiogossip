import asyncio
import collections
import fnmatch
import itertools

from .channel import Channel
from .errors import print_exception
from .gossip import Gossip


class Callback:
    def __init__(self, topic, func, loop: asyncio.AbstractEventLoop):
        self._loop = loop

        self.topic = topic
        self.func = func
        self.chan = Channel(loop=self._loop)

        self.task = self._loop.create_task(self())
        self.task.add_done_callback(print_exception)

    async def __call__(self):
        while True:
            message = await self.chan.recv()
            await self.func(message)

    async def cancel(self):
        await self.chan.close()
        self.task.cancel()


class Broker:
    def __init__(self, gossip: Gossip, loop: asyncio.AbstractEventLoop):
        self._loop = loop

        self.gossip = gossip
        self.callbacks = collections.defaultdict(list)

    async def listen(self):
        """Connect to the gossip network and start receiving messages."""
        async for message in self.gossip.recv():
            # FIXME: make messages idempotent (prevent duplicate processing)

            if "topic" not in message["metadata"]:
                continue

            topics = list(self.callbacks.keys())

            for topic in topics:
                if fnmatch.fnmatch(message["metadata"]["topic"], topic):
                    for callback in self.callbacks[topic]:
                        await callback.chan.send(message)

            for topic in topics:
                if len(self.callbacks[topic]) == 0:
                    del self.callbacks[topic]

    async def close(self):
        """Disconnect from the gossip network and stop receiving messages."""
        callbacks = [cb for cb in itertools.chain(*self.callbacks.values())]
        await asyncio.gather(*[cb.cancel() for cb in callbacks], return_exceptions=True)
        await self.gossip.close()

    def subscribe(self, topic, callback):
        """Subscribe to a topic and register a callback."""
        callback = Callback(topic, callback, loop=self._loop)
        self.callbacks[topic].append(callback)
        return callback

    async def unsubscribe(self, callback):
        """Unsubscribe from a topic and unregister a callback."""
        await callback.cancel()
        self.callbacks[callback.topic].remove(callback)

    async def publish(self, topic, message, nodes=None):
        """Publish a message to a topic."""
        # FIXME: make messages idempotent (prevent duplicate processing)
        # FIXME: allow sending to specific nodes
        message["metadata"]["topic"] = topic
        if nodes:
            for node in nodes:
                node = self.gossip.topology[node]
                await self.gossip.send(message, node)
        else:
            await self.gossip.gossip(message)
