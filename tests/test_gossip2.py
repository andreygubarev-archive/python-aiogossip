import pytest

from aiogossip.gossip2 import Gossip
from aiogossip.transport import Transport


@pytest.fixture
def peers(event_loop):
    return [
        Gossip(Transport(("localhost", 0), loop=event_loop)),
        Gossip(Transport(("localhost", 0), loop=event_loop)),
        Gossip(Transport(("localhost", 0), loop=event_loop)),
    ]


@pytest.mark.asyncio
async def test_send_and_receive(peers):
    message = {"foo": "bar"}

    await peers[0].send(message, peers[1].transport.addr)
    received_message = await anext(peers[1].recv())
    assert received_message["message"] == message
