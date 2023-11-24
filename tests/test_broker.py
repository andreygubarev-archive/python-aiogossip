import asyncio

import pytest

from aiogossip.broker import Broker


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(event_loop, gossips):
    pub = Broker(gossips[0], loop=event_loop)
    sub = Broker(gossips[1], loop=event_loop)

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

    await pub.close()
    await sub.close()
