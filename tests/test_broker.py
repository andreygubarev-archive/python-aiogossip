import asyncio

import pytest


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(event_loop, brokers):
    pub = brokers[0]
    sub = brokers[1]

    callback_message = None

    async def callback(message):
        nonlocal callback_message
        callback_message = message

    topic = "test"
    message = {"message": "foo", "metadata": {}}

    callback = sub.subscribe(topic, callback)
    try:
        async with asyncio.timeout(0.1):
            await pub.publish(topic, message)
            await sub.connect()
    except asyncio.TimeoutError:
        pass

    assert callback_message["metadata"]["topic"] == topic
    assert callback_message["message"] == message["message"]

    await sub.unsubscribe(topic, callback)
    assert callback not in sub.callbacks[topic]
    await pub.disconnect()
    await sub.disconnect()
