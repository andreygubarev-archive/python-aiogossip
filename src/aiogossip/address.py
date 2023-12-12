import dataclasses
import ipaddress


@dataclasses.dataclass(frozen=True, slots=True)
class Address:
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address
    port: int

    def __post_init__(self):
        if not isinstance(self.ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            raise TypeError("ip must be IPv4Address or IPv6Address")

        if not isinstance(self.port, int):
            raise TypeError("port must be int")

    @classmethod
    def parse_ip(
        cls, ip: str | bytes | ipaddress.IPv4Address | ipaddress.IPv6Address
    ) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        if isinstance(ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            pass
        elif isinstance(ip, (str, bytes)):
            ip = ipaddress.ip_address(ip)
        else:
            raise TypeError("ip must be str, bytes, IPv4Address or IPv6Address")

        return ip

    @classmethod
    def parse_port(cls, port: int | float | str | bytes) -> int:
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
