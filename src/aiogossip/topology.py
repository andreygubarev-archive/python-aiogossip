import uuid

import networkx as nx
import typeguard

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
