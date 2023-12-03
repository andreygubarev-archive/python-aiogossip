import collections
import ipaddress
import warnings

Address = collections.namedtuple("Address", ["ip", "port"])


def parse_addr(addr: Address | tuple | str) -> Address:
    """
    Parse the given address and return an Address object.

    Args:
        addr (Address, tuple, str): The address to parse. It can be an Address object,
            a tuple containing the IP address and port, or a string in the format "ip:port".

    Returns:
        Address: The parsed Address object.

    Raises:
        TypeError: If the address is not of type Address, tuple, or str.

    Deprecated:
        Passing a tuple or string to parse_addr is deprecated. Use Address instead.
    """
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
