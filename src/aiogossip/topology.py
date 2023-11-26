import ipaddress
import random
from typing import Iterable


class Address:
    def __init__(self, ip, port):
        self.ip = ipaddress.ip_address(ip)
        self.port = int(port)

    @property
    def addr(self):
        return (str(self.ip), self.port)

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def __eq__(self, other):
        return self.addr == other.addr

    def __hash__(self):
        return hash(self.addr)

    def __repr__(self):
        return f"<Address: {self}>"


class Node:
    def __init__(self, identity, addr):
        self.identity = identity

        self.address = None
        self.network_interface = {"local": None, "lan": None, "wan": None}
        self.set_address(addr)

    def set_address(self, addr):
        self.address = Address(*addr)

        if self.address.ip.is_loopback:
            self.network_interface["local"] = self.address
        elif self.address.ip.is_private:
            self.network_interface["lan"] = self.address

        if self.address.ip.is_global:
            self.network_interface["wan"] = self.address

    def merge_network_interface(self, other):
        if other.network_interface["local"] is not None:
            self.network_interface["local"] = other.network_interface["local"]

        if other.network_interface["lan"] is not None:
            self.network_interface["lan"] = other.network_interface["lan"]

        if other.network_interface["wan"] is not None:
            self.network_interface["wan"] = other.network_interface["wan"]

        if other.address is not None:
            self.address = other.address

    def __eq__(self, other):
        if not other:
            return False
        return self.identity == other.identity

    def __hash__(self):
        return hash(self.identity)

    def __repr__(self):
        return f"<Node: {self.identity}>"


class Topology:
    def __init__(self):
        self.node = None
        self.nodes = {}

    def add(self, nodes: Iterable[Node]):
        assert isinstance(nodes, Iterable)
        for node in nodes:
            if node == self.node:
                self.node.merge_network_interface(node)
            elif node.identity in self.nodes:
                self.nodes[node.identity].merge_network_interface(node)
            else:
                self.nodes[node.identity] = node

    def remove(self, nodes: Iterable[Node]):
        assert isinstance(nodes, Iterable)
        for node in nodes:
            if node.identity in self.nodes:
                self.nodes.pop(node.identity)

    # FIXME: get is a bad name
    # FIXME: sample is a bad name
    # FIXME: exclude is list of strings, not list of nodes
    def get(self, sample=None, exclude=None):
        nodes = [n for n in self.nodes.keys()]
        if exclude is not None:
            nodes = [n for n in nodes if n not in exclude]
        if sample is not None:
            sample = min(sample, len(nodes))
            nodes = random.sample(nodes, sample)
        return [self.nodes[n] for n in nodes]

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return node.identity in self.nodes

    def __iter__(self):
        return iter(self.nodes.values())
