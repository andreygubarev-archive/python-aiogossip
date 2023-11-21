import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport


@pytest.fixture
def peers(event_loop):
    peer1 = Gossip(Transport(("localhost", 0), loop=event_loop), [])
    peer2 = Gossip(Transport(("localhost", 0), loop=event_loop), [peer1.transport.addr])
    peer3 = Gossip(Transport(("localhost", 0), loop=event_loop), [peer1.transport.addr])
    peer4 = Gossip(
        Transport(("localhost", 0), loop=event_loop),
        [peer1.transport.addr, peer2.transport.addr],
    )
    return peer1, peer2, peer3, peer4


@pytest.mark.asyncio
async def test_send_and_receive(peers):
    message = {"message": "Hello, world!", "metadata": {}}

    await peers[0].send(message, peers[1].transport.addr)
    received_message = await anext(peers[1].recv())
    assert received_message["message"] == message["message"]
