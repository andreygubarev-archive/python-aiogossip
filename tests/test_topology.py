import ipaddress

import pytest

from aiogossip.topology import Address, Node, Topology

# Address ####################################################################


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


# Node #######################################################################


def test_node_initialization():
    node = Node("node1", ("127.0.0.1", 8000))
    assert node.identity == "node1"
    assert node.address == Address("127.0.0.1", 8000)
    assert node.network_interface["local"] == Address("127.0.0.1", 8000)
    assert node.network_interface["lan"] is None
    assert node.network_interface["wan"] is None


def test_node_set_address_local():
    node = Node("node1", ("127.0.0.1", 8000))
    node.set_address(("127.0.0.1", 8001))
    assert node.address == Address("127.0.0.1", 8001)
    assert node.network_interface["local"] == Address("127.0.0.1", 8001)
    assert node.network_interface["lan"] is None
    assert node.network_interface["wan"] is None


def test_node_set_address_lan():
    node = Node("node1", ("127.0.0.1", 8000))
    node.set_address(("192.168.1.1", 8000))
    assert node.address == Address("192.168.1.1", 8000)
    assert node.network_interface["local"] == Address("127.0.0.1", 8000)
    assert node.network_interface["lan"] == Address("192.168.1.1", 8000)
    assert node.network_interface["wan"] is None


def test_node_set_address_wan():
    node = Node("node1", ("127.0.0.1", 8000))
    node.set_address(("8.8.8.8", 8000))
    assert node.address == Address("8.8.8.8", 8000)
    assert node.network_interface["local"] == Address("127.0.0.1", 8000)
    assert node.network_interface["lan"] is None
    assert node.network_interface["wan"] == Address("8.8.8.8", 8000)


def test_node_merge_network_interface():
    node1 = Node("node1", ("127.0.0.1", 8000))
    node1.network_interface["lan"] = Address("192.168.1.2", 8000)
    node1.network_interface["wan"] = Address("192.168.1.3", 8000)

    node2 = Node("node2", ("192.168.1.1", 8000))
    node2.network_interface["lan"] = Address("192.168.1.4", 8000)
    node2.network_interface["wan"] = Address("192.168.1.5", 8000)

    node1.merge_network_interface(node2)

    assert node1.network_interface["local"] == Address("127.0.0.1", 8000)
    assert node1.network_interface["lan"] == Address("192.168.1.4", 8000)
    assert node1.network_interface["wan"] == Address("192.168.1.5", 8000)
    assert node1.address == Address("192.168.1.1", 8000)


def test_node_equality():
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node1", ("192.168.1.1", 8000))
    assert node1 == node2


def test_node_hash():
    node = Node("node1", ("127.0.0.1", 8000))
    assert hash(node) == hash("node1")


def test_node_repr():
    node = Node("node1", ("127.0.0.1", 8000))
    assert repr(node) == "<Node: node1>"


# Topology ###################################################################


def test_topology_initialization():
    topology = Topology()
    assert topology.node is None
    assert topology.nodes == {}


def test_topology_add():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    assert len(topology) == 2
    assert node1 in topology
    assert node2 in topology


def test_topology_remove():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    topology.remove([node1])
    assert len(topology) == 1
    assert node1 not in topology
    assert node2 in topology


def test_topology_get():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    nodes = topology.get()
    assert len(nodes) == 2
    assert node1 in nodes
    assert node2 in nodes


def test_topology_len():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    assert len(topology) == 2


def test_topology_contains():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1])
    assert node1 in topology
    assert node2 not in topology


def test_topology_iter():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    nodes = list(topology)
    assert len(nodes) == 2
    assert node1 in nodes
    assert node2 in nodes


def test_topology_getitem_with_node():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    assert topology[node1] == node1
    assert topology[node2] == node2


def test_topology_getitem_with_string():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    node2 = Node("node2", ("192.168.1.1", 8000))
    topology.add([node1, node2])
    assert topology["node1"] == node1
    assert topology["node2"] == node2


def test_topology_getitem_with_invalid_type():
    topology = Topology()
    node1 = Node("node1", ("127.0.0.1", 8000))
    topology.add([node1])
    with pytest.raises(TypeError):
        topology[123]
