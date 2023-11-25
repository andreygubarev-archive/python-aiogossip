import asyncio
import uuid

from .broker import Broker
from .gossip import Gossip
from .transport import Transport


class Peer:
    def __init__(self, host="0.0.0.0", port=0, identity=None, loop=None):
        # FIXME: loop shouldn't be optional
        self.loop = loop or asyncio.get_running_loop()

        self.identity = identity or uuid.uuid4().hex
        # FIXME: should be lazy
        self.transport = Transport((host, port), loop=self.loop)
        self.gossip = Gossip(self.transport, identity=self.identity)
        self.broker = Broker(self.gossip, loop=self.loop)

    @property
    def node(self):
        return self.gossip.topology.node

    async def _connect(self):
        await self.publish("connect", {"metadata": {}})

    def connect(self, nodes):
        self.gossip.topology.add(nodes)
        self.loop.create_task(self._connect())

    async def disconnect(self):
        await self.broker.disconnect()

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
        return self.loop.create_task(self.broker.connect())


# peer = Peer()

# @peer.subscribe("test")
# async def test(message):
#     print(message)

# if __name__ == "__main__":
#     peer.run_forever()
