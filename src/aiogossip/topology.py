import uuid

import networkx as nx
import typeguard

from .address import Address
from .node import Node


class Topology:
    def __init__(self):
        self.g = nx.DiGraph()

    @typeguard.typechecked
    def add_node(self, node: Node) -> None:
        """
        Adds a node to the topology.

        Args:
            node (Node): The node to be added.

        """
        if node.node_id not in self.g:
            self.g.add_node(node.node_id, node=node)

    @typeguard.typechecked
    def get_node(self, node_id: uuid.UUID) -> Node:
        """
        Retrieve a node from the topology by its ID.

        Args:
            node_id (uuid.UUID): The ID of the node to retrieve.

        Returns:
            Node: The node object.

        """
        return self.g.nodes[node_id]["node"]

    @typeguard.typechecked
    def add_route(
        self,
        snode: Node,
        saddr: Address,
        dnode: Node,
        daddr: Address,
    ) -> None:
        """
        Add a route between two nodes in the topology.

        Args:
            snode (Node): The source node.
            saddr (Address): The source address.
            dnode (Node): The destination node.
            daddr (Address): The destination address.
        """
        self.g.add_edge(snode.node_id, dnode.node_id, saddr=saddr, daddr=daddr)
