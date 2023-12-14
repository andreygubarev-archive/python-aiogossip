import math
from typing import Any

import typeguard

from .address import Address
from .node import Node
from .topology import Topology
from .transport import Transport


class Gossip:
    @typeguard.typechecked
    def __init__(self, node: Node, transport: Transport, fanout: int = 5):
        """
        Initialize a Gossip instance.

        Args:
            node (Node): The local node.
            transport (Transport): The transport layer for communication.
            fanout (int, optional): The number of nodes to gossip with. Defaults to 5.
        """
        self.node = node
        self.transport = transport
        self._fanout = fanout

        self.topology = Topology()
        self.topology.add_node(node)

    async def close(self) -> None:
        """
        Close the Gossip instance by closing the transport layer.
        """
        self.transport.close()

    @property
    def fanout(self) -> int:
        """
        Returns the minimum value between the fanout and the length of the topology.

        Returns:
            int: The minimum value between the fanout and the length of the topology.
        """
        return min(self._fanout, len(self.topology))

    @property
    def cycles(self) -> int:
        """
        Calculate the number of cycles required for gossip dissemination.

        Returns:
            int: The number of cycles required.
        """
        if self.fanout == 0:
            return 0

        if self.fanout == 1:
            return 1

        return math.ceil(math.log(len(self.topology), self.fanout))

    @typeguard.typechecked
    async def _send(self, message: Any, addr: Address) -> None:
        """
        Send a message to the specified address.

        Args:
            message (Any): The message to be sent.
            addr (Address): The address of the destination node.

        Returns:
            None
        """
        await self.transport.send(message, addr)

    @typeguard.typechecked
    async def send(self, message: Any, node: Node):
        """
        Sends a message to the specified node using the shortest route in the topology.

        Args:
            message (Any): The message to be sent.
            node (Node): The destination node.

        Returns:
            None
        """
        route = self.topology.get_shortest_route(self.node, node)
        await self._send(message, route.daddr)
