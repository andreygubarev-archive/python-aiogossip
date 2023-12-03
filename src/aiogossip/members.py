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
    INTERVAL = 1

    def __init__(self, peer):
        self.peer = peer

        self.periodic_task = self.peer._loop.create_task(self.request())
        self.periodic_task.add_done_callback(print_exception)
        self.peer.response("keepalive:*")(self.response)

    async def request(self):
        while True:
            for node in self.peer.nodes:
                await asyncio.sleep(self.INTERVAL)

                if node == self.peer.peer_id:
                    continue

                topic = "keepalive"
                message = Message()
                message.routing.src_id = self.peer.peer_id
                message.routing.dst_id = node

                response = await self.peer.request(topic, message, peers=[node], timeout=3)
                responses = []
                async for r in response:
                    responses.append(r)

                if len(responses):
                    self.peer.gossip.topology.mark_reachable(node)
                    logger.debug(f"Node is reachable: {node}")
                else:
                    self.peer.gossip.topology.mark_unreachable(node)
                    logger.debug(f"Node is unreachable: {node}")

    async def response(self, message):
        return Message()

    async def close(self):
        self.periodic_task.cancel()
        await asyncio.gather(self.periodic_task, return_exceptions=True)
