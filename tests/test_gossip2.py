import asyncio
import math
import random

import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport

random.seed(0)


@pytest.fixture(params=[1, 2, 3, 5, 10, 40, 80])
def peers(request, event_loop):
    n_peers = request.param
    n_paths = math.ceil(math.sqrt(n_peers))

    def peer():
        return Gossip(Transport(("localhost", 0), loop=event_loop), [])

    peers = [peer() for _ in range(n_peers)]
    seed = peers[0]
    for peer in peers:
        seed.peers = list(set(seed.peers) | {peer.transport.addr})
        peer.peers = {seed.transport.addr} | {
            p.transport.addr for p in random.sample(peers, n_paths)
        }
        peer.peers -= {peer.transport.addr}
        peer.peers = list(peer.peers)

    return peers


@pytest.mark.asyncio
async def test_send_and_receive(peers):
    message = {"message": "Hello, world!", "metadata": {}}
    if len(peers) == 1:
        return
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

    if len(peers) == 1:
        assert peers[0].transport.messages_received == 0
    else:
        for peer in peers:
            assert peer.transport.messages_received > 0, peer.peers
