import asyncio
import uuid

from .broker import Broker
from .gossip import Gossip
from .transport import Transport


class Peer:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        host="0.0.0.0",
        port=0,
        fanout=None,
        identity=None,
    ):
        self._loop = loop

        self.identity = identity or uuid.uuid4().hex
        # FIXME: should be lazy
        self.transport = Transport((host, port), loop=self._loop)
        self.gossip = Gossip(self.transport, fanout=fanout, identity=self.identity)
        self.broker = Broker(self.gossip, loop=self._loop)

        self.task = self._loop.create_task(self.broker.connect())

    @property
    def node(self):
        return self.gossip.topology.node

    async def _connect(self):
        message = {"metadata": {"type": "CONNECT"}}
        await self.publish("connect", message)

    def connect(self, nodes):
        self.gossip.topology.add(nodes)
        self._loop.create_task(self._connect())

    async def disconnect(self):
        await self.broker.disconnect()
        self.task.cancel()
        asyncio.gather(self.task, return_exceptions=True)

    async def publish(self, topic, message, nodes=None):
        if nodes:
            nodes = [self.gossip.topology.nodes[n] for n in nodes or []]
            await self.broker.publish(topic, message, nodes=nodes)
        else:
            await self.broker.publish(topic, message)

    def subscribe(self, topic):
        def decorator(callback):
            callback = self.broker.subscribe(topic, callback)
            return callback

        return decorator

    def run_forever(self):
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass


# peer = Peer()

# @peer.subscribe("test")
# async def test(message):
#     print(message)

# if __name__ == "__main__":
#     peer.run_forever()
