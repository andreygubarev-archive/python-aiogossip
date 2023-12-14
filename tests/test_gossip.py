import pytest

from aiogossip import gossip
from aiogossip.message import Message
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


@pytest.mark.parametrize("instances", [2])
async def test_send_message_to_node(gossip, nodes):
    snode = gossip.node
    dnode = nodes[1]
    saddr = list(snode.addresses)[0]
    daddr = list(dnode.addresses)[0]
    gossip.topology.add_node(dnode)
    gossip.topology.add_route(Route(snode, saddr, dnode, daddr))

    message = Message(snode.node_id, dnode.node_id)
    sent_message = await gossip.send(message, dnode)
    assert gossip.transport.tx_packets > 0
    assert sent_message.message_id == message.message_id
    assert sent_message.route_endpoints[-2].node == snode
    assert sent_message.route_endpoints[-2].saddr == saddr
    assert sent_message.route_endpoints[-1].node == dnode
    assert sent_message.route_endpoints[-1].daddr == daddr
