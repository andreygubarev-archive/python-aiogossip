from aiogossip.topology import Node, Topology


def test_node_initialization():
    node = Node("n1", ("127.0.0.1", 8000))
    assert node.addr == ("127.0.0.1", 8000)


def test_node_equality():
    node1 = Node("n1", ("127.0.0.1", 8000))
    node2 = Node("n1", ("127.0.0.1", 8000))
    assert node1 == node2


def test_node_hash():
    node = Node("n1", ("127.0.0.1", 8000))
    assert hash(node) == hash(("127.0.0.1", 8000))


def test_topology_initialization():
    topology = Topology()
    assert topology.nodes == []


def test_topology_set():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.set(nodes)
    assert topology.nodes == nodes


def test_topology_add():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add(node)
    assert node in topology.nodes


def test_topology_remove():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add(node)
    topology.remove(node)
    assert node not in topology.nodes


def test_topology_get():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.set(nodes)
    assert topology.get() == nodes


def test_topology_len():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.set(nodes)
    assert len(topology) == 2


def test_topology_contains():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add(node)
    assert node in topology


def test_topology_iter():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.set(nodes)
    for node in topology:
        assert node in nodes


def test_topology_get_sample():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    topology.set(nodes)
    sample = topology.get(sample=2)
    assert len(sample) == 2
    for node in sample:
        assert node in nodes
