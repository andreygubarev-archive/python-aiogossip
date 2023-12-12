import uuid

import pytest

from aiogossip.topology3 import Topology
from aiogossip.types_pb2 import Address, Endpoint, Node


@pytest.fixture
def topology():
    return Topology()


def test_add_node(topology):
    node_id = uuid.uuid4()
    topology.add_node(node_id)
    assert topology.get_node(node_id) is not None


def test_add_route(topology):
    node1 = Node(node_id=uuid.uuid4().bytes)
    node2 = Node(node_id=uuid.uuid4().bytes)
    addr1 = Address(ip=b"192.168.0.1", port=8000)
    addr2 = Address(ip=b"192.168.0.2", port=8000)

    topology.add_node(node1)
    topology.add_node(node2)
    topology.add_route(node1, addr1, node2, addr2)

    assert topology.get_route(node1, node2) == addr2


def test_add_route_latency(topology):
    node1 = Node(node_id=uuid.uuid4().bytes)
    node2 = Node(node_id=uuid.uuid4().bytes)
    latency = 0.5

    topology.add_node(node1)
    topology.add_node(node2)
    topology.add_route_latency(node1, node2, latency)

    assert topology.get_route_latency(node1, node2) == latency


def test_add_endpoint(topology):
    node = Node(node_id=uuid.uuid4().bytes)
    endpoint = Endpoint(name="endpoint1", address=Address(ip="192.168.0.1", port=8000))

    topology.add_node(node)
    topology.add_endpoint(node, endpoint)

    assert endpoint in topology.get_node(node).endpoints
