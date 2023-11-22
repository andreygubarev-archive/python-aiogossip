import asyncio
import math
import random

import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport


@pytest.fixture(params=[1, 2, 3, 5, 10], ids=lambda x: f"n_peers={x}")
def n_peers(request):
    return request.param


@pytest.fixture(params=range(5), ids=lambda x: f"seed={x}")
def rnd(request):
    random.seed(request.param)


@pytest.fixture
def peers(n_peers, rnd, event_loop):
    n_paths = math.ceil(math.sqrt(n_peers))

    def peer():
        return Gossip(transport=Transport(("localhost", 0), loop=event_loop))

    peers = [peer() for _ in range(n_peers)]
    seed = peers[0]
    for peer in peers:
        seed.topology.add(peer.transport.addr)
        peer.topology.add(seed.transport.addr)
        for p in random.sample(peers, n_paths):
            peer.topology.add(p.transport.addr)

        peer.topology.remove(peer.transport.addr)
    return peers


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

    if len(peers) == 1:
        assert peers[0].transport.messages_received == 0
    else:
        for peer in peers:
            if any([peer.transport.addr in p.topology for p in peers]):
                assert peer.transport.messages_received > 0, peer.topology
        messages_received = sum(p.transport.messages_received for p in peers)
        assert messages_received <= 2 ** len(peers)


@pytest.mark.asyncio
async def test_send_and_receive():
    peers = [Gossip(Transport(("localhost", 0)), []) for _ in range(2)]
    message = {"message": "Hello, world!", "metadata": {}}

    await peers[0].send(message, peers[1].transport.addr)
    received_message = await anext(peers[1].recv())
    assert received_message["message"] == message["message"]
