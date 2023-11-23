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
        self.addresses = {
            "local": None,
            "lan": None,
            "wan": None,
        }
        self.set_address(addr)

    def set_address(self, addr):
        self.address = Address(*addr)
        if self.address.ip.is_loopback:
            self.addresses["local"] = self.address
        elif self.address.ip.is_private:
            self.addresses["lan"] = self.address
        elif self.address.ip.is_global:
            self.addresses["wan"] = self.address

    def merge_addresses(self, other):
        if other.addresses["local"] is not None:
            self.addresses["local"] = other.addresses["local"]

        if other.addresses["lan"] is not None:
            self.addresses["lan"] = other.addresses["lan"]

        if other.addresses["wan"] is not None:
            self.addresses["wan"] = other.addresses["wan"]

        if other.address is not None:
            self.address = other.address

    def __eq__(self, other):
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
            if node.identity in self.nodes:
                self.nodes[node.identity].merge_addresses(node)
            else:
                self.nodes[node.identity] = node

    def remove(self, nodes: Iterable[Node]):
        assert isinstance(nodes, Iterable)
        for node in nodes:
            if node.identity in self.nodes:
                self.nodes.pop(node.identity)

    def get(self, sample=None):
        nodes = list(self.nodes.values())
        if sample is not None:
            nodes = random.sample(nodes, sample)
        return nodes

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return node.identity in self.nodes

    def __iter__(self):
        return iter(self.nodes.values())
