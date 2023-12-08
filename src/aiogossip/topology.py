import collections
import random
import time

import networkx as nx

from .message_pb2 import Message, Route
from .transport.address import parse_addr

Node = collections.namedtuple("Node", ["node_id", "node_addr"])


class Topology:
    def __init__(self, node_id, node_addr):
        self.g = nx.DiGraph(node_id=node_id, node_addr=node_addr)
        self.g.add_node(
            node_id,
            node_id=node_id,
            node_addr=parse_addr(node_addr),
            reachable=True,
        )

    # Node #
    @property
    def node_id(self):
        return self.g.graph["node_id"]

    @property
    def node_addr(self):
        return self.g.graph["node_addr"]

    @property
    def node(self):
        return Node(self.node_id, self.node_addr)

    # Topology #
    def add(self, nodes):
        for node in nodes:
            if node.node_id == self.node_id:
                continue

            self.g.add_node(
                node.node_id,
                node_id=node.node_id,
                node_addr=parse_addr(node.node_addr),
            )

            src = self.g.nodes[self.node_id]
            dst = self.g.nodes[node.node_id]
            self.g.add_edge(
                src["node_id"],
                dst["node_id"],
                saddr=parse_addr(src["node_addr"]),
                daddr=parse_addr(dst["node_addr"]),
            )

    def update(self, routes):
        if len(routes) < 2:
            raise ValueError("Empty route")

        nodes = set()
        for r in (r for r in routes if r.route_id not in self.g):
            self.g.add_node(r.route_id, node_id=r.route_id, node_addr=parse_addr(r.daddr or r.saddr))
            nodes.add(r.route_id)

        def edge(src, dst):
            return {
                "saddr": parse_addr(src.daddr or src.saddr),
                "daddr": parse_addr(dst.daddr or dst.saddr),
                "latency": abs(src.timestamp - dst.timestamp),
            }

        hops = ((routes[r], routes[r + 1]) for r in range(len(routes) - 1))
        for src, dst in hops:
            self.g.add_edge(src.route_id, dst.route_id, **edge(src, dst))
        self.g.add_edge(dst.route_id, src.route_id, **edge(dst, src))

        return nodes

    def sample(self, k, ignore=None):
        nodes = [e[1] for e in self.g.out_edges(self.node_id)]
        if ignore:
            nodes = list(set(nodes) - set(ignore))
        k = min(k, len(nodes))
        return random.sample(nodes, k)

    def __len__(self):
        return len(self.g)

    def __iter__(self):
        return iter(self.g.nodes)

    def __contains__(self, node_id):
        return node_id in self.g

    def __getitem__(self, node_id):
        return self.g.nodes[node_id]

    def to_dict(self):
        nodes = {}
        for node_id in self.g.nodes:
            addr = set()
            for edge in self.g.out_edges(node_id):
                saddr = self.g.edges[edge]["saddr"]
                saddr = "{}:{}".format(saddr.ip, saddr.port)
                addr.add(saddr)
            for edge in self.g.in_edges(node_id):
                daddr = self.g.edges[edge]["daddr"]
                daddr = "{}:{}".format(daddr.ip, daddr.port)
                addr.add(daddr)
            nodes[node_id.decode()] = list(addr)
        return nodes

    # Reachability #

    def mark_reachable(self, node_id):
        self.g.nodes[node_id]["reachable"] = True

    def mark_unreachable(self, node_id):
        self.g.nodes[node_id]["reachable"] = False

    # Route #
    @property
    def route(self):
        return Route(
            route_id=self.node_id,
            timestamp=int(time.time_ns()),
            saddr=f"{self.node.node_addr.ip}:{self.node.node_addr.port}",
        )

    # Addr #
    def get_addr(self, node_id):
        path = nx.shortest_path(self.g.to_undirected(), self.node_id, node_id)
        addr = self.g.edges[path[0], path[1]]["daddr"]
        return parse_addr(addr)


class Routing:
    def __init__(self, topology):
        self.topology = topology

    def set_send_route(self, message, peer_id, peer_addr):
        msg = Message()
        msg.CopyFrom(message)

        if not msg.routing.routes:
            msg.routing.routes.append(self.topology.route)

        if msg.routing.routes[-1].route_id != self.topology.node_id:
            msg.routing.routes.append(self.topology.route)

        return msg

    def set_recv_route(self, message, peer_id, peer_addr):
        msg = Message()
        msg.CopyFrom(message)

        msg.routing.routes[-1].daddr = f"{peer_addr[0]}:{peer_addr[1]}"

        if not msg.routing.routes:
            msg.routing.routes.append(self.topology.route)

        if msg.routing.routes[-1].route_id != self.topology.node_id:
            msg.routing.routes.append(self.topology.route)

        return msg
