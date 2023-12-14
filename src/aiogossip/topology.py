import uuid

import networkx as nx
import typeguard

from .node import Node
from .route import Route


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
        route: Route,
    ) -> None:
        """
        Adds a route to the topology.

        Args:
            route (Route): The route to be added.

        Returns:
            None
        """
        self.g.add_edge(route.snode.node_id, route.dnode.node_id, saddr=route.saddr, daddr=route.daddr)

    @typeguard.typechecked
    def get_route(self, snode: Node, dnode: Node) -> Route:
        """
        Retrieve a route between two nodes in the topology.

        Args:
            snode (Node): The source node.
            dnode (Node): The destination node.

        Returns:
            nx.DiGraph: The route.

        """
        return Route(
            snode=snode,
            saddr=self.g.edges[snode.node_id, dnode.node_id]["saddr"],
            dnode=dnode,
            daddr=self.g.edges[snode.node_id, dnode.node_id]["daddr"],
        )
