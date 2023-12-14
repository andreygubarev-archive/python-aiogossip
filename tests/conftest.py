import math
import random
import uuid

import pytest

from aiogossip.address import Address, to_ipaddress
from aiogossip.gossip import Gossip
from aiogossip.node import Node
from aiogossip.route import Route
from aiogossip.transport import Transport

random.seed(0)

# Generic #####################################################################


@pytest.fixture(params=[0, 1, 2, 3, 4], ids=lambda x: f"random_seed={x}")
def random_seed(request):
    random.seed(request.param)
    return request.param


@pytest.fixture(params=[1, 2, 3, 5, 10], ids=lambda x: f"instances={x}")
def instances(request):
    return request.param


# Message #####################################################################


def get_message():
    message = {}
    message["id"] = uuid.uuid4().bytes
    return message


@pytest.fixture
def message():
    return get_message()


# Address #####################################################################


def get_address(port=0):
    return Address(to_ipaddress("127.0.0.1"), port)


def get_random_address():
    return get_address(port=random.randint(0, 65535))


@pytest.fixture
def address():
    return get_address()


@pytest.fixture
def addresses(instances):
    return [get_address() for _ in range(instances)]


# Node #####################################################################


def get_node():
    node_id = uuid.uuid1()
    addresses = {get_random_address()}
    return Node(node_id, addresses)


@pytest.fixture
def node_id():
    return uuid.uuid1()


@pytest.fixture
def node():
    return get_node()


@pytest.fixture
def nodes(instances):
    return [get_node() for _ in range(instances)]


# Route #######################################################################


def get_route(snode, saddr, dnode, daddr):
    return Route(snode, saddr, dnode, daddr)


# Transport ###################################################################


def get_transport(event_loop, address):
    return Transport(address, loop=event_loop)


@pytest.fixture
def transport(event_loop, address):
    return get_transport(event_loop, address)


@pytest.fixture
def transports(event_loop, addresses):
    return [get_transport(event_loop, address) for address in addresses]


# Gossip ######################################################################


def get_gossip(node, transport, fanout=0):
    return Gossip(node, transport, fanout)


def get_random_gossip(event_loop):
    node = get_node()
    transport = get_transport(event_loop, get_address())
    node.addresses.add(transport.addr)
    return get_gossip(node, transport)


@pytest.fixture
def gossip(event_loop):
    return get_random_gossip(event_loop)


@pytest.fixture
def gossips(event_loop, instances):
    gossips = [get_random_gossip(event_loop) for _ in range(instances)]
    gossips_connections = math.ceil(math.sqrt(len(gossips)))
    for gossip in gossips:
        if gossips[0] == gossip:
            continue

        gossips[0].topology.add_node(gossip.node)
        gossips[0].topology.add_route(
            Route(
                gossips[0].node,
                list(gossips[0].node.addresses)[0],
                gossip.node,
                list(gossip.node.addresses)[0],
            )
        )

        for g in random.sample(gossips, gossips_connections):
            if g == gossip:
                continue
            gossip.topology.add_node(g.node)
            gossip.topology.add_route(
                Route(
                    gossip.node,
                    list(gossip.node.addresses)[0],
                    g.node,
                    list(g.node.addresses)[0],
                )
            )
    return gossips
