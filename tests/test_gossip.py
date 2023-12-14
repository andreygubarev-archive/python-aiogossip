from aiogossip import gossip  # noqa: F401


async def test_gossip_initialization(node, transport):
    fanout = 5
    g = gossip.Gossip(node, transport, fanout)

    assert g.node == node
    assert g.transport == transport
    assert g.fanout == fanout
    assert len(g.topology) == 1


async def test_gossip_close(node, transport):
    g = gossip.Gossip(node, transport)
    await g.close()
    assert transport.sock._closed
