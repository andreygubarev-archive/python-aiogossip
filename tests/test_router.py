import asyncio

import pytest

from aiogossip.router import Router


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(event_loop, gossips):
    sub = Router(gossips[0], loop=event_loop)

    async def callback(message):
        assert message["metadata"]["topic"] == "test"
        assert message["message"] == "foo"

    sub.subscribe("test", callback)

    pub = Router(gossips[1], loop=event_loop)
    await pub.publish("test", {"message": "foo", "metadata": {}})

    try:
        async with asyncio.timeout(0.1):
            await sub.listen()
    except asyncio.TimeoutError:
        pass

    await asyncio.sleep(0.1)
