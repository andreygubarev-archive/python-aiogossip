import collections
import random
import time

import networkx as nx

from .message_pb2 import Message, Route

Node = collections.namedtuple("Node", ["node_id", "node_addr"])


class Topology:
    def __init__(self, node_id, node_addr):
        self.graph = nx.DiGraph(node_id=node_id, node_addr=node_addr)
        self.graph.add_node(node_id, node_id=node_id, node_addr=node_addr)

    # Node #
    @property
    def node_id(self):
        return self.graph.graph["node_id"]

    @property
    def node_addr(self):
        return self.graph.graph["node_addr"]

    @property
    def node(self):
        return Node(self.node_id, self.node_addr)

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

    def update(self, routes):
        if len(routes) < 2:
            raise ValueError("Empty route")

        nodes = set()
        for r in (r for r in routes if r.route_id not in self.graph):
            self.graph.add_node(r.route_id, node_id=r.route_id, node_addr=r.daddr or r.saddr)
            nodes.add(r.route_id)

        def edge(src, dst):
            return {
                "saddr": src.daddr or src.saddr,
                "daddr": dst.daddr or dst.saddr,
                "latency": abs(src.timestamp - dst.timestamp),
            }

        hops = ((routes[r], routes[r + 1]) for r in range(len(routes) - 1))
        for src, dst in hops:
            self.graph.add_edge(src.route_id, dst.route_id, **edge(src, dst))
        self.graph.add_edge(dst.route_id, src.route_id, **edge(dst, src))

        return nodes

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

    def append_route(self, message):
        msg = Message()
        msg.CopyFrom(message)

        if not msg.routing.routes:
            msg.routing.routes.append(self.route)

        if msg.routing.routes[-1].route_id != self.node_id:
            msg.routing.routes.append(self.route)

        return msg

    # Addr #
    def get_addr(self, node_id):
        path = nx.shortest_path(self.graph.to_undirected(), self.node_id, node_id)
        return self.graph.edges[path[0], path[1]]["daddr"]
