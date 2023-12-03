import collections
import ipaddress
import warnings

Address = collections.namedtuple("Address", ["ip", "port"])


def parse_addr(addr):
    if isinstance(addr, Address):
        return addr
    elif isinstance(addr, tuple):
        warnings.warn(
            "Passing a tuple to parse_addr is deprecated, use Address instead",
            DeprecationWarning,
        )
        return Address(ipaddress.ip_address(addr[0]), int(addr[1]))
    elif isinstance(addr, str):
        warnings.warn(
            "Passing a string to parse_addr is deprecated, use Address instead",
            DeprecationWarning,
        )
        ip, port = addr.split(":")
        return Address(ipaddress.ip_address(ip), int(port))
    else:
        raise TypeError(f"Address must be a Address, tuple or str, got: {type(addr)}")
