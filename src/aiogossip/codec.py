import msgpack

from . import address


def encoder(obj):
    if isinstance(obj, address.Address):
        return msgpack.ExtType(0, msgpack.packb([obj.ip.packed, obj.port]))
    raise TypeError(f"Object of type {type(obj)} is not serializable")


def decoder(code, data):
    if code == 0:
        ip, port = msgpack.unpackb(data)
        return address.Address(ip, port)
    return msgpack.ExtType(code, data)


def packb(message):
    return msgpack.packb(message, default=encoder)


def unpackb(message):
    return msgpack.unpackb(message, ext_hook=decoder)
