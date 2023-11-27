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

    def update(self, routes):
        def add(src, dst):
            attrs = {
                "src": tuple(src[-1]),
                "dst": tuple(dst[-1]),
                "latency": abs(src[0] - dst[0]),
            }
            self.graph.add_node(src[1], node_id=src[1], node_addr=tuple(src[-1]))
            self.graph.add_node(dst[1], node_id=dst[1], node_addr=tuple(dst[-1]))
            self.graph.add_edge(src[1], dst[1], **attrs)

        connections = [(routes[i], routes[i + 1]) for i in range(len(routes) - 1)]
        dst, src = connections[-1]
        add(src, dst)
        for src, dst in connections:
            add(src, dst)

    def sample(self, k, ignore=None):
        nodes = list(self.graph.nodes)
        if ignore is not None:
            nodes = [n for n in nodes if n not in ignore]
        k = min(k, len(nodes))
        return random.sample(nodes, k)

    def __getitem__(self, node_id):
        return self.graph.nodes[node_id]

    def __len__(self):
        return len(self.graph)

    def __iter__(self):
        return iter(self.graph.nodes)

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
