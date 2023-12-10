import networkx as nx

from . import topology_pb2


class Topology:
    def __init__(self):
        self.g = nx.Graph()

    def add_node(self, node: topology_pb2.Node):
        self.g.add_node(node.id, node=node)

    def get_node(self, node_id: bytes) -> topology_pb2.Node:
        return self.g.nodes[node_id]["node"]

    def add_route(self, snode: bytes, saddr: topology_pb2.Address, dnode: bytes, daddr: topology_pb2.Address):
        self.g.add_edge(snode, dnode, saddr=saddr, daddr=daddr)

    def get_route(self, snode: bytes, dnode: bytes) -> topology_pb2.Address:
        return self.g.edges[snode, dnode]["daddr"]


class Routing:
    def __init__(self, topology):
        self.topology = topology

    def update_routes_send(self, message, peer_id, peer_addr):
        ...

    def update_routes_recv(self, message, peer_id, peer_addr):
        ...
