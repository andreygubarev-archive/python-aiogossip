import random
import time

import networkx as nx

from .message_pb2 import Route


class Topology:
    def __init__(self, node_id, node_addr):
        self.graph = nx.DiGraph(node_id=node_id, node_addr=node_addr)
        self.add([self.node])

    # Node #
    @property
    def node_id(self):
        return self.graph.graph["node_id"]

    @property
    def node_addr(self):
        return self.graph.graph["node_addr"]

    @property
    def node(self):
        return {"node_id": self.node_id, "node_addr": tuple(self.node_addr)}

    # Topology #
    def add(self, nodes):
        for node in nodes:
            self.graph.add_node(node["node_id"], **node)

            if node["node_id"] == self.node_id:
                continue

            src = self.graph.nodes[self.node_id]
            dst = self.graph.nodes[node["node_id"]]
            attrs = {
                "saddr": tuple(src["node_addr"]),
                "daddr": tuple(dst["node_addr"]),
                "latency": 0,
            }
            self.graph.add_edge(src["node_id"], dst["node_id"], **attrs)

    def sample(self, k, ignore=None):
        nodes = [e[1] for e in self.graph.out_edges(self.node_id)]
        if ignore:
            nodes = list(set(nodes) - set(ignore))
        k = min(k, len(nodes))
        return random.sample(nodes, k)

    def __getitem__(self, node_id):
        return self.graph.nodes[node_id]

    def __len__(self):
        return len(self.graph)

    def __iter__(self):
        return iter(self.graph.nodes)

    def __contains__(self, node_id):
        return node_id in self.graph

    # Route #
    @property
    def route(self):
        r = Route()
        r.route_id = self.node_id
        r.timestamp = int(time.time_ns())
        r.saddr = f"{self.node_addr[0]}:{self.node_addr[1]}"
        return r

    def set_route(self, message):
        if not message.metadata.route:
            message.metadata.route.append(self.route)

        if message.metadata.route[-1].route_id != self.node_id:
            message.metadata.route.append(self.route)

        return message

    def update_routes(self, message):
        if len(message.metadata.route) < 2:
            raise ValueError("Empty route")

        nodes = set()
        for r in (r for r in message.metadata.route if r.route_id not in self.graph):
            self.graph.add_node(r.route_id, node_id=r.route_id, node_addr=r.daddr or r.saddr)
            nodes.add(r.route_id)

        def edge(src, dst):
            return {
                "saddr": src.daddr or src.saddr,
                "daddr": dst.daddr or dst.saddr,
                "latency": abs(src.timestamp - dst.timestamp),
            }

        hops = (
            (message.metadata.route[r], message.metadata.route[r + 1]) for r in range(len(message.metadata.route) - 1)
        )
        for src, dst in hops:
            self.graph.add_edge(src.route_id, dst.route_id, **edge(src, dst))
        self.graph.add_edge(dst.route_id, src.route_id, **edge(dst, src))

        return nodes

    # Addr #
    def get_addr(self, node_id):
        path = nx.shortest_path(self.graph.to_undirected(), self.node_id, node_id)
        return self.graph.edges[path[0], path[1]]["daddr"]
