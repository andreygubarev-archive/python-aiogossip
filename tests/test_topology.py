import ipaddress

from aiogossip.topology import Address, Node, Topology


def test_address_initialization():
    address = Address("127.0.0.1", 8000)
    assert address.ip == ipaddress.ip_address("127.0.0.1")
    assert address.port == 8000


def test_address_addr_property():
    address = Address("127.0.0.1", 8000)
    assert address.addr == ("127.0.0.1", 8000)


def test_address_str_representation():
    address = Address("127.0.0.1", 8000)
    assert str(address) == "127.0.0.1:8000"


def test_address_equality():
    address1 = Address("127.0.0.1", 8000)
    address2 = Address("127.0.0.1", 8000)
    assert address1 == address2


def test_address_hash():
    address = Address("127.0.0.1", 8000)
    assert hash(address) == hash(("127.0.0.1", 8000))


def test_address_repr():
    address = Address("127.0.0.1", 8000)
    assert repr(address) == "<Address: 127.0.0.1:8000>"


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


def test_node_repr():
    node = Node("n1", ("127.0.0.1", 8000))
    assert repr(node) == "<Node: n1>"


def test_topology_initialization():
    topology = Topology()
    assert topology.nodes == []


def test_topology_set():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.add(nodes)
    assert topology.nodes == nodes


def test_topology_add():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add([node])
    assert node in topology.nodes


def test_topology_remove():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add([node])
    topology.remove([node])
    assert node not in topology.nodes


def test_topology_get():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.add(nodes)
    assert topology.get() == nodes


def test_topology_len():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.add(nodes)
    assert len(topology) == 2


def test_topology_contains():
    topology = Topology()
    node = ("127.0.0.1", 8000)
    topology.add([node])
    assert node in topology


def test_topology_iter():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001)]
    topology.add(nodes)
    for node in topology:
        assert node in nodes


def test_topology_get_sample():
    topology = Topology()
    nodes = [("127.0.0.1", 8000), ("127.0.0.1", 8001), ("127.0.0.1", 8002)]
    topology.add(nodes)
    sample = topology.get(sample=2)
    assert len(sample) == 2
    for node in sample:
        assert node in nodes
