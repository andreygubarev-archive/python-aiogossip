import asyncio

from .errors import print_exception
from .message_pb2 import Message


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

                topic = "keepalive:{}".format(node)
                message = Message()

                response = await self.peer.request(topic, message, peers=[node], timeout=3)
                responses = []
                async for r in response:
                    responses.append(r)

                if len(responses) == 0:
                    print("Node {} is dead".format(node))

                await asyncio.sleep(1)

    async def response(self, message):
        return message