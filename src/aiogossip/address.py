import dataclasses
import ipaddress


@dataclasses.dataclass(frozen=True, slots=True)
class Address:
    """
    Represents a network address consisting of an IP address and a port number.
    """

    ip: ipaddress.IPv4Address | ipaddress.IPv6Address
    port: int

    def __post_init__(self):
        if not isinstance(self.ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            raise TypeError("ip must be IPv4Address or IPv6Address")

        if not isinstance(self.port, int):
            raise TypeError("port must be int")


def to_ipaddress(
    ip: str | bytes | ipaddress.IPv4Address | ipaddress.IPv6Address,
) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """
    Convert the given IP address representation to an instance of `ipaddress.IPv4Address` or `ipaddress.IPv6Address`.

    Args:
        ip (str | bytes | ipaddress.IPv4Address | ipaddress.IPv6Address): The IP address representation.

    Returns:
        ipaddress.IPv4Address | ipaddress.IPv6Address: The converted IP address.

    Raises:
        TypeError: If the `ip` argument is not of type `str`, `bytes`, `IPv4Address`, or `IPv6Address`.
    """
    if isinstance(ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        pass
    elif isinstance(ip, (str, bytes)):
        ip = ipaddress.ip_address(ip)
    else:
        raise TypeError("ip must be str, bytes, IPv4Address or IPv6Address")

    return ip


def to_port(port: int | float | str | bytes) -> int:
    """
    Convert the given port to an integer.

    Args:
        port (int | float | str | bytes): The port to be converted.

    Returns:
        int: The converted port.

    Raises:
        ValueError: If the port is not a digit when it is a string or bytes.
        TypeError: If the port is not an int, float, string, or bytes.
        ValueError: If the port is not between 0 and 65535.

    """
    if isinstance(port, int):
        pass
    elif isinstance(port, float):
        port = int(port)
    elif isinstance(port, (str, bytes)):
        if port.isdigit():
            port = int(port)
        else:
            raise ValueError("port must be digit")
    else:
        raise TypeError("port must be int")

    if not 0 <= port <= 65535:
        raise ValueError("port must be between 0 and 65535")

    return port
