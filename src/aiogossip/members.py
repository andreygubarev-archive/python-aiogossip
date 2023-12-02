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
                topic = "keepalive:{}".format(node["node_id"].decode())
                message = Message()
                response = await self.peer.request(topic, message, timeout=3)

                responses = []
                async for response in response:
                    responses.append(response)

                if len(responses) == 0:
                    print("Node {} is dead".format(node["node_id"].decode()))

                await asyncio.sleep(1)

    async def response(self, message):
        return message
