import dataclasses
import ipaddress


@dataclasses.dataclass
class Address:
    ip: ipaddress.IPv4Address | ipaddress.IPv6Address
    port: int

    def __post_init__(self):
        if isinstance(self.ip, (str, bytes)):
            self.ip = ipaddress.ip_address(self.ip)
        if not isinstance(self.ip, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            raise TypeError("ip must be IPv4Address or IPv6Address")

        if isinstance(self.port, float):
            self.port = int(self.port)
        elif isinstance(self.port, str) and self.port.isdigit():
            self.port = int(self.port)
        if not isinstance(self.port, int):
            raise TypeError("port must be int")
