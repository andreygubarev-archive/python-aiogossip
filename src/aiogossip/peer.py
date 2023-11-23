import asyncio

from .gossip import Gossip
from .router import Router
from .transport import Transport


class Peer:
    def __init__(self, bind, identity=None):
        self.identity = None

        self.transport = Transport(bind)
        self.gossip = Gossip(self.transport, identity=self.identity)
        self.router = Router(self.gossip)

    def subscribe(self, topic):
        def decorator(callback):
            self.router.subscribe(topic, callback)

        return decorator

    def run_forever(self):
        asyncio.run(self.router.listen())


# peer = Peer(("localhost", 8000))

# @peer.subscribe("test")
# async def test(message):
#     print(message)

# if __name__ == "__main__":
#     peer.run_forever()
