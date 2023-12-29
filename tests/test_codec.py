# MODULE: aiogossip.codec
import ipaddress
import uuid

from aiogossip import codec
from aiogossip.types import address, endpoint, peer_endpoint


def test_codec():
    message = {
        "address": address.to_address("127.0.0.1:1337"),
        "endpoint": endpoint.Endpoint(),
        "ipaddress": ipaddress.ip_address("127.0.0.1"),
        "peer_endpoint": peer_endpoint.PeerEndpoint(uuid.uuid1(), endpoint.Endpoint()),
        "set": set([1, 2, 3]),
        "uuid": uuid.uuid4(),
    }

    packed = codec.packb(message)
    unpacked = codec.unpackb(packed)

    assert message == unpacked
