import uuid

import networkx as nx

from . import topology_pb2


class Topology:
    def __init__(self):
        self.g = nx.Graph()

    def add_node(self, node: bytes | uuid.UUID | topology_pb2.Node):
        if isinstance(node, bytes):
            node = topology_pb2.Node(node_id=node)
        elif isinstance(node, uuid.UUID):
            node = topology_pb2.Node(node_id=node.bytes)
        elif isinstance(node, topology_pb2.Node):
            pass
        else:
            raise TypeError(f"Unknown node type {type(node)}")

        if node.node_id not in self.g:
            self.g.add_node(node.node_id, node=node)

    def get_node(self, node_id: bytes | uuid.UUID) -> topology_pb2.Node:
        if isinstance(node_id, bytes):
            pass
        elif isinstance(node_id, uuid.UUID):
            node_id = node_id.bytes
        else:
            raise TypeError(f"Unknown node type {type(node_id)}")

        return self.g.nodes[node_id]["node"]

    def add_route(
        self,
        snode: bytes | uuid.UUID | topology_pb2.Node,
        saddr: topology_pb2.Address,
        dnode: bytes | uuid.UUID | topology_pb2.Node,
        daddr: topology_pb2.Address,
    ):
        if not isinstance(snode, topology_pb2.Node):
            snode = self.get_node(snode)
        if not isinstance(dnode, topology_pb2.Node):
            dnode = self.get_node(dnode)

        self.g.add_edge(snode.node_id, dnode.node_id, saddr=saddr, daddr=daddr)

    def get_route(
        self, snode: bytes | uuid.UUID | topology_pb2.Node, dnode: bytes | uuid.UUID | topology_pb2.Node
    ) -> topology_pb2.Address:
        if not isinstance(snode, topology_pb2.Node):
            snode = self.get_node(snode)
        if not isinstance(dnode, topology_pb2.Node):
            dnode = self.get_node(dnode)

        return self.g.edges[snode.node_id, dnode.node_id]["daddr"]

    def add_route_latency(
        self, snode: bytes | uuid.UUID | topology_pb2.Node, dnode: bytes | uuid.UUID | topology_pb2.Node, latency: float
    ):
        if not isinstance(snode, topology_pb2.Node):
            snode = self.get_node(snode)
        if not isinstance(dnode, topology_pb2.Node):
            dnode = self.get_node(dnode)

        self.g.edges[snode, dnode]["latency"] = latency

    def get_route_latency(
        self, snode: bytes | uuid.UUID | topology_pb2.Node, dnode: bytes | uuid.UUID | topology_pb2.Node
    ) -> float:
        if not isinstance(snode, topology_pb2.Node):
            snode = self.get_node(snode)
        if not isinstance(dnode, topology_pb2.Node):
            dnode = self.get_node(dnode)

        return self.g.edges[snode, dnode]["latency"]

    def add_endpoint(self, node: bytes | uuid.UUID | topology_pb2.Node, endpoint: topology_pb2.Endpoint):
        if not isinstance(node, topology_pb2.Node):
            node = self.get_node(node)

        if endpoint not in node.endpoints:
            node.endpoints.append(endpoint)


# class Routing:
#     def __init__(self, topology):
#         self.topology = topology

#     def update_routes_send(self, message, peer_id, peer_addr):
#         ...

#     def update_routes_recv(self, message, peer_id, peer_addr):
#         ...
