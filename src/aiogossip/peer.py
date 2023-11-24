import asyncio
import uuid

from .gossip import Gossip
from .router import Router
from .transport import Transport


class Peer:
    def __init__(self, host="0.0.0.0", port=0, identity=None, loop=None):
        self.loop = loop or asyncio.get_running_loop()

        self.identity = identity or uuid.uuid4().hex

        self.transport = Transport((host, port), loop=self.loop)
        self.gossip = Gossip(self.transport, identity=self.identity)
        self.router = Router(self.gossip, loop=self.loop)

    def subscribe(self, topic):
        def decorator(callback):
            self.router.subscribe(topic, callback)

        return decorator

    def run_forever(self):
        asyncio.run(self.router.listen())


# peer = Peer()

# @peer.subscribe("test")
# async def test(message):
#     print(message)

# if __name__ == "__main__":
#     peer.run_forever()
