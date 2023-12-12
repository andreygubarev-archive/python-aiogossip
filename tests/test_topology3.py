# import ipaddress

# import pytest

# from aiogossip.topology3 import Topology
# from aiogossip.topology_pb2 import Address, Endpoint, Node


# @pytest.fixture
# def topology():
#     return Topology()


# def test_add_node(topology):
#     node = Node(id=b"node1")
#     topology.add_node(node)
#     assert topology.get_node(b"node1") == node


# def test_add_route(topology):
#     snode = b"src"
#     dnode = b"dst"
#     saddr = ipaddress.ip_address("127.0.0.1")
#     saddr = Address(ip=saddr.packed, port=8000)
#     daddr = ipaddress.ip_address("127.0.0.1")
#     daddr = Address(ip=daddr.packed, port=9000)
#     topology.add_route(snode, saddr, dnode, daddr)
#     assert topology.get_route(snode, dnode) == daddr


# def test_get_route(topology):
#     snode = b"src"
#     dnode = b"dst"
#     saddr = ipaddress.ip_address("127.0.0.1")
#     saddr = Address(ip=saddr.packed, port=8000)
#     daddr = ipaddress.ip_address("127.0.0.1")
#     daddr = Address(ip=daddr.packed, port=9000)
#     topology.add_route(snode, saddr, dnode, daddr)
#     assert topology.get_route(snode, dnode) == daddr


# def test_add_endpoint(topology):
#     node = Node(id=b"node1")
#     addr = ipaddress.ip_address("127.0.0.1")
#     addr = Address(ip=addr.packed, port=8000)
#     endpoint = Endpoint(addr=addr)
#     topology.add_node(node)
#     topology.add_endpoint(b"node1", endpoint)
#     assert topology.get_node(b"node1").endpoints[0] == endpoint
