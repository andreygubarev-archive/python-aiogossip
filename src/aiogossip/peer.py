import asyncio
import uuid

from . import config
from .broker import Broker
from .errors import print_exception
from .gossip import Gossip
from .transport import Transport


class Peer:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        host="0.0.0.0",
        port=0,
        fanout=None,
        node_id=None,
    ):
        self._loop = loop or asyncio.get_event_loop()

        self.node_id = node_id or uuid.uuid4().hex
        # FIXME: should be lazy
        self.transport = Transport((host, port), loop=self._loop)
        self.gossip = Gossip(self.transport, fanout=fanout, node_id=self.node_id)
        self.broker = Broker(self.gossip, loop=self._loop)

        self.task = self._loop.create_task(self.broker.listen())
        self.task.add_done_callback(print_exception)

    @property
    def node(self):
        return self.gossip.topology.node

    @property
    def DSN(self):
        return "{}@{}:{}".format(self.node["node_id"], *self.node["node_addr"])

    @property
    def nodes(self):
        return list(self.gossip.topology)

    async def _connect(self):
        topic = "connect:{}".format(uuid.uuid4().hex)
        message = {"metadata": {}}

        response = await self.publish(topic, message, syn=True)
        async for r in response:
            pass

    def connect(self, seeds=config.GOSSIP_SEEDS):
        if not seeds:
            return

        nodes = []

        if isinstance(seeds, str):
            seeds = seeds.split(",")
            for seed in seeds:
                node_id, addr = seed.split("@")
                host, port = addr.split(":")
                nodes.append({"node_id": node_id, "node_addr": (host, int(port))})

        elif isinstance(seeds, list):
            nodes = seeds

        self.gossip.topology.add(nodes)
        task = self._loop.create_task(self._connect())
        task.add_done_callback(print_exception)

    async def disconnect(self):
        await self.broker.close()
        self.task.cancel()
        await asyncio.gather(self.task, return_exceptions=True)

    async def publish(self, topic, message, peers=None, syn=False):
        topic = topic.replace("{uuid}", uuid.uuid4().hex)

        if syn:
            message["metadata"]["syn"] = self.node_id
        return await self.broker.publish(topic, message, node_ids=peers)

    def subscribe(self, topic):
        def decorator(callback):
            callback = self.broker.subscribe(topic, callback)
            return callback

        return decorator

    async def request(self, topic, message, peers=None, timeout=5):
        topic = "request:{}:{}".format(topic, uuid.uuid4().hex)
        response = await self.publish(topic, message, peers=peers, syn=True)
        return response

    def response(self, topic):
        topic = "request:{}:*".format(topic)

        async def responder(message, r):
            await self.publish(
                message["metadata"]["topic"], r, peers=[message["metadata"]["syn"]]
            )

        def decorator(callback):
            callback = self.broker.subscribe(topic, callback)
            callback._handler = responder
            return callback

        return decorator

    def run_forever(self, main=None):  # pragma: no cover
        if main:
            self._loop.run_until_complete(main())

        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.run_until_complete(self.disconnect())
