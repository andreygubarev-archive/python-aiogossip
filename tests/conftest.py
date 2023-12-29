import random
import uuid

import pytest

from aiogossip.types.address import Address, to_ipaddress
from aiogossip.types.endpoint import Endpoint
from aiogossip.types.peer_endpoint import PeerEndpoint

random.seed(0)

# Random ######################################################################


@pytest.fixture(params=[0, 1, 2, 3, 4], ids=lambda x: f"random_seed={x}")
def random_seed(request):
    random.seed(request.param)
    return request.param


@pytest.fixture(params=[1, 2, 3, 5, 10], ids=lambda x: f"instances={x}")
def instances(request):
    return request.param


# Address #####################################################################


def get_address(address="127.0.0.1", port=0):
    return Address(to_ipaddress(address), port)


@pytest.fixture
def address():
    return get_address(address="127.0.0.1", port=1337)


@pytest.fixture
def addresses(instances):
    return [get_address() for _ in range(instances)]


# Endpoint ####################################################################


def get_endpoint(saddr=None, daddr=None):
    return Endpoint(saddr, daddr)


@pytest.fixture
def endpoint(address):
    return get_endpoint(saddr=address, daddr=address)


@pytest.fixture
def endpoints(instances):
    return [get_endpoint() for _ in range(instances)]


# PeerEndpoint ################################################################


def get_peer_endpoint(id, endpoint):
    return PeerEndpoint(id, endpoint)


@pytest.fixture
def peer_endpoint(endpoint):
    return get_peer_endpoint(uuid.uuid1(), endpoint)
