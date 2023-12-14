import pytest

from aiogossip import gossip  # noqa: F401
from aiogossip.route import Route


async def test_gossip_initialization(node, transport):
    fanout = 5
    g = gossip.Gossip(node, transport, fanout)

    assert g.node == node
    assert g.transport == transport
    assert g._fanout == fanout
    assert len(g.topology) == 1


async def test_gossip_close(node, transport):
    g = gossip.Gossip(node, transport)
    await g.close()
    assert transport.sock._closed


async def test_gossip_fanout(node, transport):
    fanout = 5
    g = gossip.Gossip(node, transport, fanout)
    assert g.fanout == 1


@pytest.mark.parametrize("instances", [50])
async def test_gossip_cycles(node, transport, nodes):
    assert gossip.Gossip(node, transport, 0).cycles == 0
    assert gossip.Gossip(node, transport, 1).cycles == 1

    g = gossip.Gossip(node, transport, 5)
    for node in nodes[:5]:
        g.topology.add_node(node)
    assert g.cycles == 2

    g = gossip.Gossip(node, transport, 5)
    for node in nodes[:15]:
        g.topology.add_node(node)
    assert g.cycles == 2

    g = gossip.Gossip(node, transport, 5)
    for node in nodes[:25]:
        g.topology.add_node(node)
    assert g.cycles == 2

    g = gossip.Gossip(node, transport, 5)
    for node in nodes[:50]:
        g.topology.add_node(node)
    assert g.cycles == 3


async def test_send_message(gossip, address):
    message = "Hello, World!"
    await gossip._send(message, address)
    assert gossip.transport.tx_packets > 0


@pytest.mark.parametrize("instances", [2])
async def test_send_message_to_node(gossip, nodes):
    gossip.topology.add_node(nodes[1])
    saddr = list(gossip.node.addresses)[0]
    daddr = list(nodes[1].addresses)[0]
    gossip.topology.add_route(Route(gossip.node, saddr, nodes[1], daddr))
    message = "Hello, World!"
    await gossip.send(message, nodes[1])
    assert gossip.transport.tx_packets > 0
