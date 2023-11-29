import random
import time

import networkx as nx


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
                "src": tuple(src["node_addr"]),
                "dst": tuple(dst["node_addr"]),
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
        return [time.time_ns(), self.node_id, self.node_addr]

    def set_route(self, message):
        route = message["metadata"].get("route", [self.route])
        if route[-1][1] != self.graph.graph["node_id"]:
            route.append(self.route)
        message["metadata"]["route"] = route
        return message

    def update_routes(self, route):
        if len(route) < 2:
            raise ValueError("Empty route")

        nodes = set()
        for r in (r for r in route if r[1] not in self.graph):
            self.graph.add_node(r[1], node_id=r[1], node_addr=r[-1])
            nodes.add(r[1])

        def edge(src, dst):
            return {"src": src[-1], "dst": dst[-1], "latency": abs(src[0] - dst[0])}

        hops = ((route[r], route[r + 1]) for r in range(len(route) - 1))
        for src, dst in hops:
            self.graph.add_edge(src[1], dst[1], **edge(src, dst))
        self.graph.add_edge(dst[1], src[1], **edge(dst, src))

        return nodes

    # Addr #
    def get_addr(self, node_id):
        path = nx.shortest_path(self.graph.to_undirected(), self.node_id, node_id)
        return self.graph.edges[path[0], path[1]]["dst"]
