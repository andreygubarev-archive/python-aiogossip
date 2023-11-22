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
