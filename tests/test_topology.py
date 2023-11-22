from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology()
    assert topology.nodes == []


def test_topology_set():
    topology = Topology()
    nodes = [("localhost", 8000), ("localhost", 8001)]
    topology.set(nodes)
    assert topology.nodes == nodes


def test_topology_add():
    topology = Topology()
    node = ("localhost", 8000)
    topology.add(node)
    assert node in topology.nodes


def test_topology_remove():
    topology = Topology()
    node = ("localhost", 8000)
    topology.add(node)
    topology.remove(node)
    assert node not in topology.nodes


def test_topology_get():
    topology = Topology()
    nodes = [("localhost", 8000), ("localhost", 8001)]
    topology.set(nodes)
    assert topology.get() == nodes


def test_topology_len():
    topology = Topology()
    nodes = [("localhost", 8000), ("localhost", 8001)]
    topology.set(nodes)
    assert len(topology) == 2


def test_topology_contains():
    topology = Topology()
    node = ("localhost", 8000)
    topology.add(node)
    assert node in topology


def test_topology_iter():
    topology = Topology()
    nodes = [("localhost", 8000), ("localhost", 8001)]
    topology.set(nodes)
    for node in topology:
        assert node in nodes


def test_topology_get_sample():
    topology = Topology()
    nodes = [("localhost", 8000), ("localhost", 8001), ("localhost", 8002)]
    topology.set(nodes)
    sample = topology.get(sample=2)
    assert len(sample) == 2
    for node in sample:
        assert node in nodes
