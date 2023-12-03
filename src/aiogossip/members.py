import asyncio
import logging
import sys

from . import config
from .errors import print_exception
from .message_pb2 import Message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
if config.DEBUG:
    logger.setLevel(logging.DEBUG)  # pragma: no cover


class Members:
    SCHEDULER_INTERVAL = 5

    KEEPALIVE_INTERVAL = 15
    KEEPALIVE_TIMEOUT = 5

    def __init__(self, peer):
        self.peer = peer

        self.keepalive_tasks = {}

        self.keepalive_scheduler_task = self.peer._loop.create_task(self.keepalive_scheduler())
        self.keepalive_scheduler_task.add_done_callback(print_exception)
        self.peer.response("keepalive:*")(self.pong)

    async def keepalive(self, peer_id):
        while True:
            topic = "keepalive"
            message = Message()
            message.routing.src_id = self.peer.peer_id
            message.routing.dst_id = peer_id

            response = await self.peer.request(topic, message, peers=[peer_id], timeout=self.KEEPALIVE_TIMEOUT)
            responses = []
            async for r in response:
                responses.append(r)

            if len(responses):
                self.peer.gossip.topology.mark_reachable(peer_id)
                logger.debug(f"Node is reachable: {peer_id}")
            else:
                self.peer.gossip.topology.mark_unreachable(peer_id)
                logger.debug(f"Node is unreachable: {peer_id}")

            await asyncio.sleep(self.KEEPALIVE_INTERVAL)

    async def keepalive_scheduler(self):
        while True:
            for node in self.peer.nodes:
                if node == self.peer.peer_id:
                    continue

                if node not in self.keepalive_tasks:
                    self.keepalive_tasks[node] = self.peer._loop.create_task(self.keepalive(node))
                    self.keepalive_tasks[node].add_done_callback(print_exception)

            await asyncio.sleep(self.SCHEDULER_INTERVAL)

    async def pong(self, message):
        return Message()

    async def close(self):
        self.keepalive_scheduler_task.cancel()
        await asyncio.gather(self.keepalive_scheduler_task, return_exceptions=True)

        for task in self.keepalive_tasks.values():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
