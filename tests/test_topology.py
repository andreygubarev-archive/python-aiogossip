import networkx as nx
import pytest

from aiogossip.route import Route
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


@pytest.mark.parametrize("instances", [2])
def test_topology_add_route(nodes, addresses):
    topology = Topology()

    nodes[0].addresses.add(addresses[0])
    topology.add_node(nodes[0])

    nodes[1].addresses.add(addresses[1])
    topology.add_node(nodes[1])

    route = Route(nodes[0], addresses[0], nodes[1], addresses[1])
    topology.add_route(route)

    assert topology.g.has_edge(nodes[0].node_id, nodes[1].node_id)
    assert topology.g.edges[nodes[0].node_id, nodes[1].node_id]["saddr"] == addresses[0]
    assert topology.g.edges[nodes[0].node_id, nodes[1].node_id]["daddr"] == addresses[1]


@pytest.mark.parametrize("instances", [2])
def test_topology_get_route(nodes, addresses):
    topology = Topology()

    nodes[0].addresses.add(addresses[0])
    topology.add_node(nodes[0])

    nodes[1].addresses.add(addresses[1])
    topology.add_node(nodes[1])

    route = Route(nodes[0], addresses[0], nodes[1], addresses[1])
    topology.add_route(route)

    retrieved_route = topology.get_route(nodes[0], nodes[1])

    assert retrieved_route.snode == nodes[0]
    assert retrieved_route.saddr == addresses[0]
    assert retrieved_route.dnode == nodes[1]
    assert retrieved_route.daddr == addresses[1]
