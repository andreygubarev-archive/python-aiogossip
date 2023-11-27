import asyncio
import uuid

from .broker import Broker
from .errors import print_exception
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

        self.task = self._loop.create_task(self.broker.listen())
        self.task.add_done_callback(print_exception)

    @property
    def node(self):
        return self.gossip.topology.node

    async def _connect(self):
        message = {"metadata": {"type": "CONNECT"}}
        await self.publish("connect", message)

    def connect(self, nodes):
        self.gossip.topology.add(nodes)
        task = self._loop.create_task(self._connect())
        task.add_done_callback(print_exception)

    async def disconnect(self):
        await self.broker.close()
        self.task.cancel()
        await asyncio.gather(self.task, return_exceptions=True)

    async def publish(self, topic, message, nodes=None):
        await self.broker.publish(topic, message, nodes=nodes)

    def subscribe(self, topic):
        def decorator(callback):
            callback = self.broker.subscribe(topic, callback)
            return callback

        return decorator

    def run_forever(self):  # pragma: no cover
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.run_until_complete(self.disconnect())
