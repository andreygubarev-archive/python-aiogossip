import ipaddress
import uuid

import pytest

from aiogossip import address, codec
from aiogossip.endpoint import Endpoint
from aiogossip.message import Message


@pytest.mark.parametrize("instances", [2])
def test_packb(gossips):
    ip = ipaddress.IPv4Address("127.0.0.1")
    port = 8080
    addr = address.Address(ip, port)
    identifier = uuid.uuid4()

    message = Message(
        route_snode=gossips[0].node,
        route_dnode=gossips[1].node,
    )

    data = {
        "addr": addr,
        "identifier": identifier,
        "test": "test",
        "node": gossips[0].node,
        "endpoint": Endpoint(node=gossips[0].node),
        "message": message,
    }

    packed = codec.packb(data)
    assert isinstance(packed, bytes)

    upacked = codec.unpackb(packed)
    assert upacked["addr"].ip == ip
    assert upacked["addr"].port == port
    assert upacked["identifier"] == identifier
    assert upacked["test"] == "test"
    assert upacked["node"] == gossips[0].node
