import asyncio
from unittest.mock import MagicMock

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


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_connect_ignores_messages_without_topic(event_loop, brokers):
    broker = brokers[0]

    async def recv():
        yield {"metadata": {}, "message": "foo"}

    broker.gossip.recv = recv

    callback = MagicMock()
    callback = broker.subscribe("test", callback)
    callback.chan.send = MagicMock()

    try:
        async with asyncio.timeout(0.1):
            await broker.connect()
    except asyncio.TimeoutError:
        pass

    callback.chan.send.assert_not_called()
    await broker.disconnect()
