import asyncio

import pytest


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_peer(peers):
    peer1 = peers[0]
    assert peer1.node_id is not None
    peer2 = peers[1]
    assert peer2.node_id is not None
    assert peer1.node_id != peer2.node_id

    peer1.connect([peer2.node])
    assert peer2.node_id in peer1.gossip.topology

    message = {"message": "Hello, world!", "metadata": {}}
    await peer1.publish("test", message)

    handler_message = None

    @peer2.subscribe("test")
    async def handler(message):
        nonlocal handler_message
        handler_message = message["message"]

    await asyncio.sleep(0.1)
    assert handler_message == message["message"]

    for peer in peers:
        await peer.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_peer_publish_ack(peers):
    peers[0].connect([peers[1].node])
    await asyncio.sleep(0.1)

    message = {"metadata": {}}
    response = await peers[0].publish("topic", message, syn=True)

    messages = []
    async for message in response:
        messages.append(message)

    assert len(messages) == 1
    assert messages[0]["metadata"]["syn"] == peers[0].node_id
    assert messages[0]["metadata"]["ack"] == peers[1].node_id

    for peer in peers:
        await peer.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [3])
@pytest.mark.asyncio
async def test_peer_forwarding(peers):
    peers[0].connect([peers[1].node])
    peers[1].connect([peers[2].node])

    handler_message = None
    subscribe = peers[0].subscribe("test")

    @subscribe
    async def handler(message):
        nonlocal handler_message
        handler_message = message["message"]

    await asyncio.sleep(0.1)

    message = {"message": "Hello, world!", "metadata": {}}
    await peers[2].publish("test", message, peers=[peers[0].node_id])

    await asyncio.sleep(0.1)
    assert handler_message == message["message"]

    for peer in peers:
        await peer.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [3])
@pytest.mark.asyncio
async def test_peer_reverse_forwarding(peers):
    peers[0].connect([peers[1].node])
    peers[1].connect([peers[2].node])
    await asyncio.sleep(0.1)

    handler_message = None
    subscribe = peers[2].subscribe("test")

    @subscribe
    async def handler(message):
        nonlocal handler_message
        handler_message = message["message"]

    message = {"message": "Hello, world!", "metadata": {}}
    await peers[0].publish("test", message, peers=[peers[2].node_id])

    await asyncio.sleep(0.1)
    assert handler_message == message["message"]

    for peer in peers:
        await peer.disconnect()
