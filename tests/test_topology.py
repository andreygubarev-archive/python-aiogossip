import pytest

from aiogossip.message_pb2 import Route
from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology(b"node1", ("localhost", 8000))
    assert topology.node_id == b"node1"
    assert topology.node_addr == ("localhost", 8000)


def test_topology_add():
    topology = Topology("node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    assert len(topology) == 2


def test_topology_update_route(message):
    topology = Topology("node1", ("localhost", 8000))
    message.metadata.route.append(
        Route(
            route_id=b"node1",
            saddr="localhost:8000",
            daddr="localhost:8000",
        )
    )

    message.metadata.route.append(
        Route(
            route_id=b"node1",
            saddr="localhost:8001",
        )
    )

    topology.update_route(message)
    assert len(topology) == 2


def test_topology_update_route_invalid(message):
    topology = Topology(b"node1", ("localhost", 8000))
    with pytest.raises(ValueError):
        message.metadata.route.append(
            Route(
                route_id=b"node1",
                saddr="localhost:8000",
                daddr="localhost:8000",
            )
        )
        topology.update_route(message)


def test_topology_sample():
    topology = Topology(b"node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    sample = topology.sample(1)
    assert len(sample) == 1
    assert sample[0] in ["node1", "node2"]


def test_topology_getitem():
    topology = Topology("node1", ("localhost", 8000))
    assert topology["node1"]["node_id"] == "node1"


def test_topology_route():
    topology = Topology(b"node1", ("localhost", 8000))
    assert topology.route.route_id == b"node1"
    assert topology.route.saddr == "localhost:8000"


def test_topology_set_route(message):
    topology = Topology(b"node1", ("localhost", 8000))
    message = topology.set_route(message)
    assert len(message.metadata.route) == 1


def test_topology_get_addr():
    topology = Topology(b"node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    addr = topology.get_addr("node2")
    assert addr == ("localhost", 8001)
