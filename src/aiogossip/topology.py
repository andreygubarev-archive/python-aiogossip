import random


class Topology:
    def __init__(self, peers=None):
        self.peers = peers or []

    def set(self, peers):
        self.peers = peers

    def add(self, peer):
        if peer not in self.peers:
            self.peers.append(peer)

    def remove(self, peer):
        if peer in self.peers:
            self.peers.remove(peer)

    def get(self, sample=None):
        if sample is not None:
            return random.sample(self.peers, sample)
        else:
            return self.peers

    def __len__(self):
        return len(self.peers)

    def __contains__(self, peer):
        return peer in self.peers

    def __iter__(self):
        return iter(self.peers)
