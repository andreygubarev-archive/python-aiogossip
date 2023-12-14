import dataclasses

from .address import Address
from .node import Node


@dataclasses.dataclass(frozen=True, slots=True)
class Endpoint:
    node: Node

    saddr: Address
    daddr: Address

    def __post_init__(self):
        if not isinstance(self.node, Node):
            raise TypeError("node must be Node")

        if not isinstance(self.saddr, Address):
            raise TypeError("saddr must be Address")

        if not isinstance(self.daddr, Address):
            raise TypeError("daddr must be Address")