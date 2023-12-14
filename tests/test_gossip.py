import pytest

from aiogossip import gossip  # noqa: F401


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
