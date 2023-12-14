# FILEPATH: /Users/andrey/Workspace/Development/andreygubarev/python-aiogossip/tests/test_codec.py

import ipaddress
import uuid

from aiogossip import address, codec


def test_packb(node):
    # Test with IPv4Address
    ip = ipaddress.IPv4Address("127.0.0.1")
    port = 8080
    addr = address.Address(ip, port)
    identifier = uuid.uuid4()

    data = {"addr": addr, "identifier": identifier, "test": "test", "node": node}

    packed = codec.packb(data)
    assert isinstance(packed, bytes)

    upacked = codec.unpackb(packed)
    assert upacked["addr"].ip == ip
    assert upacked["addr"].port == port
    assert upacked["identifier"] == identifier
    assert upacked["test"] == "test"
    assert upacked["node"] == node
