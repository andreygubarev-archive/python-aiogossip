import pytest

from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology("node1", ("localhost", 8000))
    assert topology.node_id == "node1"
    assert topology.node_addr == ("localhost", 8000)


def test_topology_add():
    topology = Topology("node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    assert len(topology) == 2


def test_topology_update_routes():
    topology = Topology("node1", ("localhost", 8000))
    topology.update_routes(
        [
            (0, "node2", ("localhost", 8001), ("localhost", 8001)),
            (0, "node1", ("localhost", 8000)),
        ]
    )
    assert len(topology) == 2


def test_topology_update_routes_invalid():
    topology = Topology("node1", ("localhost", 8000))
    with pytest.raises(ValueError):
        topology.update_routes(
            [
                (0, "node2", ("localhost", 8001), ("localhost", 8001)),
            ]
        )


def test_topology_sample():
    topology = Topology("node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    sample = topology.sample(1)
    assert len(sample) == 1
    assert sample[0] in ["node1", "node2"]


def test_topology_getitem():
    topology = Topology("node1", ("localhost", 8000))
    assert topology["node1"]["node_id"] == "node1"


def test_topology_route():
    topology = Topology("node1", ("localhost", 8000))
    assert len(topology.route) == 3
    assert topology.route[1] == "node1"


def test_topology_set_route():
    topology = Topology("node1", ("localhost", 8000))
    message = {"metadata": {}}
    topology.set_route(message)
    assert "route" in message["metadata"]


def test_topology_get_addr():
    topology = Topology("node1", ("localhost", 8000))
    topology.add([{"node_id": "node2", "node_addr": ("localhost", 8001)}])
    addr = topology.get_addr("node2")
    assert addr == ("localhost", 8001)
