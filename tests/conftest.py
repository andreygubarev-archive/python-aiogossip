import random
import uuid

import pytest

from aiogossip.address import Address, to_ipaddress
from aiogossip.transport import Transport

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


def get_address():
    return Address(to_ipaddress("127.0.0.1"), 0)


@pytest.fixture
def address():
    return Address(to_ipaddress("127.0.0.1"), 0)


@pytest.fixture
def addresses(instances):
    return [get_address() for _ in range(instances)]


# Transport ###################################################################


def get_transport(event_loop, address):
    return Transport(address, loop=event_loop)


@pytest.fixture
def transport(event_loop, address):
    return get_transport(event_loop, address)


@pytest.fixture
def transports(event_loop, addresses):
    return [get_transport(event_loop, address) for address in addresses]
