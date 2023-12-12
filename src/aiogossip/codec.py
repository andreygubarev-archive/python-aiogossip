import dataclasses
import ipaddress
import uuid

import msgpack

from . import address


def encoder(obj):
    if isinstance(obj, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        return msgpack.ExtType(0, bytes(obj.packed))
    if isinstance(obj, uuid.UUID):
        return msgpack.ExtType(1, bytes(obj.bytes))
    if isinstance(obj, address.Address):
        return msgpack.ExtType(2, packb(dataclasses.asdict(obj)))
    raise TypeError(f"Object of type {type(obj)} is not serializable")


def decoder(code, data):
    if code == 0:
        return ipaddress.ip_address(data)
    if code == 1:
        return uuid.UUID(bytes=data)
    if code == 2:
        return address.Address(**unpackb(data))
    return msgpack.ExtType(code, data)


def packb(message):
    return msgpack.packb(message, default=encoder)


def unpackb(message):
    return msgpack.unpackb(message, ext_hook=decoder)
