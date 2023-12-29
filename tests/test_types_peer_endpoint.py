# MODULE: aiogossip.types.peer_endpoint

import ipaddress
import uuid

import pytest

from aiogossip.types.address import Address
from aiogossip.types.endpoint import Endpoint
from aiogossip.types.peer_endpoint import PeerEndpoint


def test_peer_endpoint_init_with_valid_arguments():
    id = uuid.uuid1()
    saddr = Address(ipaddress.IPv4Address("192.168.1.1"), 8080)
    daddr = Address(ipaddress.IPv4Address("192.168.1.2"), 8080)
    endpoint = Endpoint(saddr, daddr)
    peer_endpoint = PeerEndpoint(id, endpoint)
    assert peer_endpoint.id == id
    assert peer_endpoint.endpoint == endpoint


def test_peer_endpoint_init_with_invalid_id():
    id = "invalid_id"
    saddr = Address(ipaddress.IPv4Address("192.168.1.1"), 8080)
    daddr = Address(ipaddress.IPv4Address("192.168.1.2"), 8080)
    endpoint = Endpoint(saddr, daddr)
    with pytest.raises(TypeError):
        PeerEndpoint(id, endpoint)


def test_peer_endpoint_init_with_invalid_id_version():
    id = uuid.uuid4()
    saddr = Address(ipaddress.IPv4Address("192.168.1.1"), 8080)
    daddr = Address(ipaddress.IPv4Address("192.168.1.2"), 8080)
    endpoint = Endpoint(saddr, daddr)
    with pytest.raises(ValueError):
        PeerEndpoint(id, endpoint)


def test_peer_endpoint_init_with_invalid_endpoint():
    id = uuid.uuid1()
    endpoint = "invalid_endpoint"
    with pytest.raises(TypeError):
        PeerEndpoint(id, endpoint)
