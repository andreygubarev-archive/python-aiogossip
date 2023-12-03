import pytest

from aiogossip.message_pb2 import Route
from aiogossip.topology import Node, Topology
from aiogossip.transport import Address, Transport


def test_topology(topology):
    assert isinstance(topology, Topology)
    assert isinstance(topology.node, Node)
    assert isinstance(topology.node_id, bytes)
    assert isinstance(topology.node_addr, Address)


def test_topology_add(topology):
    topology.add([{"node_id": topology.node_id, "node_addr": topology.node_addr}])
    topology.add([{"node_id": "node2", "node_addr": ("127.0.0.1", 8001)}])
    assert len(topology) == 2


def test_topology_update_route(topology, message):
    message.routing.routes.append(
        Route(
            route_id=b"node1",
            saddr="127.0.0.1:8000",
            daddr="127.0.0.1:8000",
        )
    )

    message.routing.routes.append(
        Route(
            route_id=b"node1",
            saddr="127.0.0.1:8001",
        )
    )

    topology.update(message.routing.routes)
    assert len(topology) == 2


def test_topology_update_route_invalid(topology, message):
    with pytest.raises(ValueError):
        message.routing.routes.append(
            Route(
                route_id=b"node1",
                saddr="127.0.0.1:8000",
                daddr="127.0.0.1:8000",
            )
        )
        topology.update(message.routing.routes)


def test_topology_sample(topology):
    topology.add([{"node_id": "node2", "node_addr": ("127.0.0.1", 8002)}])
    topology.add([{"node_id": "node3", "node_addr": ("127.0.0.1", 8003)}])
    sample = topology.sample(1, ignore=["node3"])
    assert len(sample) == 1
    assert sample[0] in ["node1", "node2"]


def test_topology_iter(topology):
    topology.add([{"node_id": "node2", "node_addr": ("127.0.0.1", 8002)}])
    assert list(topology) == [topology.node_id, "node2"]


def test_topology_getitem():
    topology = Topology("node1", Transport.parse_addr("127.0.0.1:8000"))
    assert topology["node1"]["node_id"] == "node1"


def test_topology_contains():
    topology = Topology("node1", Transport.parse_addr("127.0.0.1:8000"))
    assert "node1" in topology


def test_topology_route():
    topology = Topology(b"node1", Transport.parse_addr("127.0.0.1:8000"))
    assert topology.route.route_id == b"node1"
    assert topology.route.saddr == "127.0.0.1:8000"


def test_topology_set_route(message):
    topology = Topology(b"node1", Transport.parse_addr("127.0.0.1:8000"))
    message = topology.append_route(message)
    assert len(message.routing.routes) == 1


def test_topology_get_addr():
    topology = Topology(b"node1", Transport.parse_addr("127.0.0.1:8000"))
    topology.add([{"node_id": "node2", "node_addr": ("127.0.0.1", 8001)}])
    addr = topology.get_addr("node2")
    assert addr == ("127.0.0.1", 8001)
