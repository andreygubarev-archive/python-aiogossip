import dataclasses
import ipaddress
import uuid

import msgpack

from . import address, endpoint, message, node


def encoder(obj):
    if isinstance(obj, set):
        return msgpack.ExtType(0, packb(list(obj)))
    if isinstance(obj, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        return msgpack.ExtType(1, bytes(obj.packed))
    if isinstance(obj, uuid.UUID):
        return msgpack.ExtType(2, bytes(obj.bytes))
    if isinstance(obj, address.Address):
        return msgpack.ExtType(3, packb(dataclasses.astuple(obj)))
    if isinstance(obj, node.Node):
        return msgpack.ExtType(4, packb(dataclasses.astuple(obj)))
    if isinstance(obj, endpoint.Endpoint):
        return msgpack.ExtType(5, packb(dataclasses.astuple(obj)))
    if isinstance(obj, message.Message):
        return msgpack.ExtType(6, packb(dataclasses.asdict(obj)))
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
        return node.Node(*unpackb(data))
    if code == 5:
        return endpoint.Endpoint(*unpackb(data))
    if code == 6:
        return message.Message(**unpackb(data))
    return msgpack.ExtType(code, data)  # pragma: no cover


def packb(message):
    return msgpack.packb(message, default=encoder)


def unpackb(message):
    return msgpack.unpackb(message, ext_hook=decoder)
