import random


class Topology:
    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def set(self, nodes):
        self.nodes = nodes

    def add(self, peer):
        if peer not in self.nodes:
            self.nodes.append(peer)

    def remove(self, peer):
        if peer in self.nodes:
            self.nodes.remove(peer)

    def get(self, sample=None):
        if sample is not None:
            return random.sample(self.nodes, sample)
        else:
            return self.nodes

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, peer):
        return peer in self.nodes

    def __iter__(self):
        return iter(self.nodes)
