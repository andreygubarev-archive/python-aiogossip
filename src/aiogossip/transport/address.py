import collections
import ipaddress

Address = collections.namedtuple("Address", ["ip", "port"])


def parse_addr(addr):
    if isinstance(addr, Address):
        return addr
    elif isinstance(addr, tuple):
        return Address(ipaddress.ip_address(addr[0]), int(addr[1]))
    elif isinstance(addr, str):
        ip, port = addr.split(":")
        return Address(ipaddress.ip_address(ip), int(port))
    else:
        raise TypeError(f"Address must be a Address, tuple or str, got: {type(addr)}")
