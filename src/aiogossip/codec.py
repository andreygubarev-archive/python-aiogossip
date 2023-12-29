import dataclasses
import ipaddress
import uuid

import msgpack

from .types import address, endpoint, peer_endpoint


def astuple(dataclass: dataclasses.dataclass):
    """
    Convert a dataclass instance to a tuple without recursive conversion.

    Args:
        dataclass: The dataclass instance to convert.

    Returns:
        tuple: The converted tuple.
    """
    return tuple(getattr(dataclass, f.name) for f in dataclasses.fields(dataclass))


def encoder(obj):
    if isinstance(obj, set):
        return msgpack.ExtType(0, packb(list(obj)))
    if isinstance(obj, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        return msgpack.ExtType(1, bytes(obj.packed))
    if isinstance(obj, uuid.UUID):
        return msgpack.ExtType(2, bytes(obj.bytes))
    if isinstance(obj, address.Address):
        return msgpack.ExtType(3, packb(astuple(obj)))
    if isinstance(obj, endpoint.Endpoint):
        return msgpack.ExtType(4, packb(astuple(obj)))
    if isinstance(obj, peer_endpoint.PeerEndpoint):
        return msgpack.ExtType(5, packb(astuple(obj)))
    raise TypeError(f"Object of type {type(obj)} is not serializable")  # pragma: no cover


def decoder(code, data):
    if code == 0:
        return set(unpackb(data))
    if code == 1:
        return ipaddress.ip_address(data)
    if code == 2:
        return uuid.UUID(bytes=data)
    if code == 3:
        return address.Address(*unpackb(data))
    if code == 4:
        return endpoint.Endpoint(*unpackb(data))
    if code == 5:
        return peer_endpoint.PeerEndpoint(*unpackb(data))
    return msgpack.ExtType(code, data)  # pragma: no cover


def packb(message):
    return msgpack.packb(message, default=encoder, use_bin_type=False)


def unpackb(message):
    return msgpack.unpackb(message, ext_hook=decoder)
