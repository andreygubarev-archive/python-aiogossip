import asyncio
from unittest.mock import MagicMock

import pytest


class AsyncMagicMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMagicMock, self).__call__(*args, **kwargs)


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(brokers):
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

    await sub.unsubscribe(callback)
    assert callback not in sub.callbacks[topic]
    await pub.disconnect()
    await sub.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_connect_ignores_messages_without_topic(brokers):
    broker = brokers[0]

    async def recv():
        yield {"metadata": {}, "message": "foo"}

    broker.gossip.recv = recv

    callback = MagicMock()
    callback = broker.subscribe("test", callback)
    callback.chan.send = MagicMock()

    await broker.connect()
    callback.chan.send.assert_not_called()
    await broker.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_connect_cleans_up_empty_topics(brokers):
    broker = brokers[0]
    topic = "test"

    async def recv():
        yield {"metadata": {"topic": topic}}

    broker.gossip.recv = recv

    callback = broker.subscribe(topic, MagicMock())
    assert topic in broker.callbacks
    await broker.unsubscribe(callback)
    assert topic in broker.callbacks
    assert len(broker.callbacks[topic]) == 0

    await broker.connect()
    assert topic not in broker.callbacks
    await broker.disconnect()


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_wildcard_topic(brokers):
    broker = brokers[0]
    topic = "test.*"

    async def recv():
        yield {"metadata": {"topic": "test.1"}}
        yield {"metadata": {"topic": "test.2"}}

    broker.gossip.recv = recv

    callback = MagicMock()
    callback = broker.subscribe(topic, callback)
    callback.chan.send = AsyncMagicMock()

    await broker.connect()
    assert callback.chan.send.call_count == 2
    await broker.disconnect()
