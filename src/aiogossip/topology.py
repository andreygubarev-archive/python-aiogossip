import collections.abc
import ipaddress
import random


class Node:
    def __init__(self, identity, addr):
        self.identity = identity
        ip, port = addr
        self.ip = ipaddress.ip_address(ip)
        self.port = int(port)

    @property
    def addr(self):
        return (str(self.ip), self.port)

    def __eq__(self, other):
        return self.addr == other.addr

    def __hash__(self):
        return hash(self.addr)

    def __repr__(self):
        return f"<Node: {self.identity}>"


class Topology:
    def __init__(self):
        self.node = None
        self.nodes = []

    def add(self, nodes):
        assert isinstance(nodes, collections.abc.Iterable)
        for node in nodes:
            if node not in self.nodes:
                self.nodes.append(node)

    def remove(self, nodes):
        assert isinstance(nodes, collections.abc.Iterable)
        for node in nodes:
            if node in self.nodes:
                self.nodes.remove(node)

    def get(self, sample=None):
        if sample is not None:
            return random.sample(self.nodes, sample)
        else:
            return self.nodes

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return node in self.nodes

    def __iter__(self):
        return iter(self.nodes)
