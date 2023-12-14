import networkx as nx

from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology()
    assert isinstance(topology.g, nx.DiGraph), "Topology.g should be an instance of nx.DiGraph"


def test_topology_initialization_empty():
    topology = Topology()
    assert len(topology.g.nodes) == 0, "Topology.g should be initialized with no nodes"
    assert len(topology.g.edges) == 0, "Topology.g should be initialized with no edges"
