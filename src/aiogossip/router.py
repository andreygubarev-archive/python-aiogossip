from .gossip import Gossip


class Router:
    def __init__(self, gossip: Gossip):
        self.gossip = gossip

    async def publish(self):
        pass

    async def subscribe(self):
        pass
