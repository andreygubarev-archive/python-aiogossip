import random
import uuid

import pytest

from aiogossip.address import Address, to_ipaddress
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
