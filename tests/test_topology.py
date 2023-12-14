import networkx as nx

from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology()
    assert isinstance(topology.g, nx.DiGraph)


def test_topology_initialization_empty():
    topology = Topology()
    assert len(topology.g.nodes) == 0
    assert len(topology.g.edges) == 0


def test_add_node(node):
    topology = Topology()
    topology.add_node(node)
    assert node.node_id in topology.g
    assert topology.g.nodes[node.node_id]["node"] == node


def test_topology_get_node(node):
    topology = Topology()
    topology.add_node(node)
    assert topology.get_node(node.node_id) == node
