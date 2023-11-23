import asyncio

import pytest

from aiogossip.router import Router


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(event_loop, gossips):
    sub = Router(gossips[0], loop=event_loop)
    pub = Router(gossips[1], loop=event_loop)

    callback_message = None

    async def callback(message):
        nonlocal callback_message
        callback_message = message

    topic = "test"
    message = {"message": "foo", "metadata": {}}

    try:
        async with asyncio.timeout(0.1):
            sub.subscribe(topic, callback)
            await pub.publish(topic, message)
            await sub.listen()
    except asyncio.TimeoutError:
        pass

    assert callback_message["metadata"]["topic"] == topic
    assert callback_message["message"] == message["message"]
