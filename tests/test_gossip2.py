import asyncio
import math
import random

import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport

random.seed(0)


@pytest.fixture
def peers(event_loop):
    n_peers = 15
    n_paths = math.ceil(math.sqrt(n_peers))

    def peer():
        return Gossip(Transport(("localhost", 0), loop=event_loop), [])

    peers = [peer() for _ in range(n_peers)]
    seed = peers[0].transport.addr
    for peer in peers:
        peer.peers = {seed} | {p.transport.addr for p in random.sample(peers, n_paths)}
        peer.peers -= {peer.transport.addr}
        peer.peers = list(peer.peers)

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

    async def listener(peer):
        try:
            async with asyncio.timeout(0.1):
                async for message in peer.recv():
                    pass
        except asyncio.TimeoutError:
            pass

    tasks = [asyncio.create_task(listener(peer)) for peer in peers]
    await asyncio.gather(*tasks)

    for peer in peers:
        assert peer.transport.messages_received > 0, peer.peers
