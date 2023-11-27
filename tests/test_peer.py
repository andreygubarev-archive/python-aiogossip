import asyncio

import pytest


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_peer(peers):
    peer1 = peers[0]
    assert peer1.identity is not None
    peer2 = peers[1]
    assert peer2.identity is not None
    assert peer1.identity != peer2.identity

    peer1.connect([peer2.node])
    assert peer2.identity in peer1.gossip.topology

    message = {"message": "Hello, world!", "metadata": {}}
    await peer1.publish("test", message)

    callback_message = None

    @peer2.subscribe("test")
    async def handler(message):
        nonlocal callback_message
        callback_message = message["message"]

    await asyncio.sleep(0.1)
    assert callback_message == message["message"]

    for peer in peers:
        await peer.disconnect()
