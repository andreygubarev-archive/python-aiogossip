import math

import typeguard

from .endpoint import Endpoint
from .message import Message, update_recv_endpoints, update_send_endpoints
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
    async def send(self, message: Message, node: Node) -> Message:
        route = self.topology.get_shortest_route(self.node, node)
        message = update_send_endpoints(
            message,
            send=Endpoint(route.snode, saddr=route.saddr),
            recv=Endpoint(route.dnode, daddr=route.daddr),
        )
        await self.transport.send(message, route.daddr)
        return message

    @typeguard.typechecked
    async def recv(self) -> Message:
        while True:
            message, addr = await self.transport.recv()
            message = update_recv_endpoints(
                message,
                send=Endpoint(message.route_endpoints[-2].node, daddr=addr),
                recv=Endpoint(message.route_endpoints[-1].node, saddr=self.transport.addr),
            )
            yield message
