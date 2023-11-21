import asyncio
import random

import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport

random.seed(42)


@pytest.fixture
def peers(event_loop):
    n_peers = 5

    def peer():
        return Gossip(Transport(("localhost", 0), loop=event_loop), [])

    peers = [peer() for _ in range(n_peers)]
    for peer in peers:
        peer.peers = [p.transport.addr for p in random.sample(peers, 3)]
        if peer.transport.addr in peer.peers:
            peer.peers.remove(peer.transport.addr)

    return peers


@pytest.mark.asyncio
async def test_send_and_receive(peers):
    message = {"message": "Hello, world!", "metadata": {}}

    await peers[0].send(message, peers[1].transport.addr)
    received_message = await anext(peers[1].recv())
    assert received_message["message"] == message["message"]


@pytest.mark.asyncio
async def test_gossip(peers):
    message = {"message": "Hello, world!", "metadata": {}}

    await peers[0].gossip(message)
    assert message["metadata"]["type"] == "gossip"
    assert message["metadata"]["hops"] == 1

    async def listener(peer):
        async for message in peer.recv():
            return message

    tasks = [asyncio.create_task(listener(peer)) for peer in peers]
    await asyncio.sleep(0.1)

    async with asyncio.timeout(1):
        await asyncio.gather(*tasks)
