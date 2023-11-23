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
    def __init__(self, identity, local=None, lan=None, wan=None):
        self.identity = identity

        self._local = Address(*local) if local else None
        self._lan = Address(*lan) if lan else None
        self._wan = Address(*wan) if wan else None

        self._connection = self._local or self._lan or self._wan

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, addr):
        ip, port = addr
        ip = ipaddress.ip_address(ip)
        port = int(port)

        if ip.is_loopback:
            self.local = addr
            self._connection = self.local
        elif ip.is_private:
            self.lan = addr
            self._connection = self.lan
        elif ip.is_global:
            self.wan = addr
            self._connection = self.wan
        else:
            raise ValueError(f"Invalid IP address: {ip}")

    @property
    def local(self):
        return self._local

    @local.setter
    def local(self, addr):
        self._local = Address(*addr)

    @property
    def lan(self):
        return self._lan

    @lan.setter
    def lan(self, addr):
        self._lan = Address(*addr)

    @property
    def wan(self):
        return self._wan

    @wan.setter
    def wan(self, addr):
        self._wan = Address(*addr)

    def merge(self, other):
        if other.local:
            self.local = other.local.addr
        if other.lan:
            self.lan = other.lan.addr
        if other.wan:
            self.wan = other.wan.addr
        if other.connection:
            self.connection = other.connection.addr

    def __eq__(self, other):
        return self.identity == other.identity

    def __hash__(self):
        return hash(self.identity)

    def __repr__(self):
        return f"<Node: {self.identity}>"


class Topology:
    def __init__(self):
        self.node = None
        self.nodes = []

    def add(self, nodes: Iterable[Node]):
        assert isinstance(nodes, Iterable)
        for node in nodes:
            if node in self.nodes:
                self.nodes[self.nodes.index(node)].merge(node)
            else:
                self.nodes.append(node)

    def remove(self, nodes: Iterable[Node]):
        assert isinstance(nodes, Iterable)
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
