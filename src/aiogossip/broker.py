import asyncio
import collections
import itertools

from .channel import Channel
from .gossip import Gossip


class Broker:
    def __init__(self, gossip: Gossip, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.gossip = gossip
        self.chan = collections.defaultdict(Channel)
        self.subs = collections.defaultdict(list)

    async def connect(self):
        """Connect to the gossip network and start receiving messages."""
        async for message in self.gossip.recv():
            # FIXME: handle messages with no topic
            # FIXME: implement ventilator pattern
            await self.chan[message["metadata"]["topic"]].send(message)

    async def disconnect(self):
        """Disconnect from the gossip network and stop receiving messages."""
        tasks = list(itertools.chain(*self.subs.values()))
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.gossip.close()

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

    def unsubscribe(self, topic, callback):
        raise NotImplementedError

    async def publish(self, topic, message, nodes=None):
        message["metadata"]["topic"] = topic
        await self.gossip.gossip(message)
