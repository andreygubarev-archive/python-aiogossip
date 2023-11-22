from aiogossip.topology import Topology


def test_topology_initialization():
    topology = Topology()
    assert topology.peers == []


def test_topology_set():
    topology = Topology()
    peers = [("localhost", 8000), ("localhost", 8001)]
    topology.set(peers)
    assert topology.peers == peers


def test_topology_add():
    topology = Topology()
    peer = ("localhost", 8000)
    topology.add(peer)
    assert peer in topology.peers


def test_topology_remove():
    topology = Topology()
    peer = ("localhost", 8000)
    topology.add(peer)
    topology.remove(peer)
    assert peer not in topology.peers


def test_topology_get():
    topology = Topology()
    peers = [("localhost", 8000), ("localhost", 8001)]
    topology.set(peers)
    assert topology.get() == peers


def test_topology_get_sample():
    topology = Topology()
    peers = [("localhost", 8000), ("localhost", 8001), ("localhost", 8002)]
    topology.set(peers)
    sample = topology.get(sample=2)
    assert len(sample) == 2
    for peer in sample:
        assert peer in peers
