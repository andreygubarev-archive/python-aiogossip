import math
import random

import pytest

from aiogossip.broker import Broker
from aiogossip.gossip import Gossip
from aiogossip.transport import Transport


@pytest.fixture(params=range(5), ids=lambda x: f"randomize={x}")
def randomize(request):
    random.seed(request.param)


@pytest.fixture(params=[1, 2, 3, 5, 10, 25], ids=lambda x: f"instances={x}")
def instances(request):
    return request.param


@pytest.fixture
def gossips(randomize, event_loop, instances):
    def get_gossip():
        transport = Transport(("localhost", 0), loop=event_loop)
        return Gossip(transport=transport)

    connections = math.ceil(math.sqrt(instances))
    gossips = [get_gossip() for _ in range(instances)]
    seed = gossips[0]
    for gossip in gossips:
        seed.topology.add([gossip.topology.node])

        gossip.topology.add([seed.topology.node])
        for g in random.sample(gossips, connections):
            gossip.topology.add([g.topology.node])

        gossip.topology.remove([gossip.topology.node])
    return gossips


@pytest.fixture
def brokers(randomize, event_loop, instances, gossips):
    brokers = [Broker(gossip, loop=event_loop) for gossip in gossips]
    return brokers
