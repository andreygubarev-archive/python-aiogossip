import math
import random

import pytest

from aiogossip.broker import Broker
from aiogossip.gossip import Gossip
from aiogossip.peer import Peer
from aiogossip.transport import Transport


@pytest.fixture(params=[0, 1, 2, 3, 4], ids=lambda x: f"random_seed={x}")
def random_seed(request):
    random.seed(request.param)
    return request.param


@pytest.fixture(params=[1, 2, 3, 5, 10, 50], ids=lambda x: f"instances={x}")
def instances(request):
    return request.param


def get_transport(event_loop):
    return Transport(("localhost", 0), loop=event_loop)


@pytest.fixture
def transport(event_loop):
    return get_transport(event_loop)


@pytest.fixture
def transports(event_loop, instances):
    return [get_transport(event_loop) for _ in range(instances)]


@pytest.fixture
def gossips(random_seed, event_loop, instances):
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

    return gossips


@pytest.fixture
def brokers(random_seed, event_loop, instances, gossips):
    brokers = [Broker(gossip, loop=event_loop) for gossip in gossips]
    return brokers


@pytest.fixture
def peers(random_seed, event_loop, instances):
    peers = [Peer(loop=event_loop) for _ in range(instances)]
    return peers
