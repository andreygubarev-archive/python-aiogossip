import math
import random

import pytest

from aiogossip.gossip import Gossip
from aiogossip.transport import Transport


@pytest.fixture(params=range(5), ids=lambda x: f"seed={x}")
def rnd(request):
    random.seed(request.param)


@pytest.fixture(params=[1, 2, 3, 5, 10, 25], ids=lambda x: f"n_gossips={x}")
def n_gossips(request):
    return request.param


@pytest.fixture
def gossips(event_loop, rnd, n_gossips):
    def get_gossip():
        transport = Transport(("localhost", 0), loop=event_loop)
        return Gossip(transport=transport)

    n_connections = math.ceil(math.sqrt(n_gossips))
    gossips = [get_gossip() for _ in range(n_gossips)]
    seed = gossips[0]
    for gossip in gossips:
        seed.topology.add([gossip.topology.node])

        gossip.topology.add([seed.topology.node])
        for g in random.sample(gossips, n_connections):
            gossip.topology.add([g.topology.node])

        gossip.topology.remove([gossip.topology.node])
    return gossips
