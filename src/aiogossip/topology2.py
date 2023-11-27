import random
import time

import networkx as nx


class Topology:
    def __init__(self, identity, addr):
        self.graph = nx.DiGraph(identity=identity, addr=addr)

    @property
    def node(self):
        return (self.graph.graph["identity"], self.graph.graph["addr"])

    @property
    def route(self):
        return (self.graph.graph["identity"], time.time_ns(), self.graph.graph["addr"])

    def set_route(self, message):
        route = message["metadata"].get("route", [self.route])
        if route[-1][0] != self.graph.graph["identity"]:
            route.append(self.route)
        message["metadata"]["route"] = route
        return message

    def get_node(self, identity):
        return self.graph.nodes[identity]

    def add(self, nodes):
        for node in nodes:
            identity, addr = node
            self.graph.add_node(identity, identity=identity, addr=addr)

    def sample(self, k, ignore=None):
        nodes = list(self.graph.nodes)
        if ignore is not None:
            nodes = [n for n in nodes if n not in ignore]
        k = min(k, len(nodes))
        return random.sample(nodes, k)

    def update(self, routes):
        def add_edge(src, dst):
            latency = abs(src[1] - dst[1])
            self.graph.add_edge(
                src[0], dst[0], src=src[-1], dst=dst[-1], latency=latency
            )

        connections = [(routes[i], routes[i + 1]) for i in range(len(routes) - 1)]

        dst, src = connections[-1]
        add_edge(src, dst)

        for src, dst in connections:
            add_edge(src, dst)

    def __getitem__(self, node_id):
        return self.graph.nodes[node_id]

    def __len__(self):
        return len(self.graph)

    def __iter__(self):
        return iter(self.graph.nodes)
