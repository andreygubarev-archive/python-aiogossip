import asyncio
from unittest.mock import MagicMock

import pytest


class AsyncMagicMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMagicMock, self).__call__(*args, **kwargs)


@pytest.mark.parametrize("random_seed", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_subscribe(brokers):
    pub = brokers[0]
    sub = brokers[1]

    handler_message = None

    async def handler(message):
        nonlocal handler_message
        handler_message = message

    topic = "test"
    message = {"message": "foo", "metadata": {}}

    handler = sub.subscribe(topic, handler)
    try:
        async with asyncio.timeout(0.1):
            await pub.publish(topic, message)
            await sub.listen()
    except asyncio.TimeoutError:
        pass

    assert handler_message["metadata"]["topic"] == topic
    assert handler_message["message"] == message["message"]

    await sub.unsubscribe(handler)
    assert handler not in sub._handlers[topic]
    await pub.close()
    await sub.close()


@pytest.mark.parametrize("random_seed", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_connect_ignores_messages_without_topic(brokers):
    broker = brokers[0]

    async def recv():
        yield {"metadata": {}, "message": "foo"}

    broker.gossip.recv = recv

    handler = MagicMock()
    handler = broker.subscribe("test", handler)
    handler.chan.send = MagicMock()

    await broker.listen()
    handler.chan.send.assert_not_called()
    await broker.close()


@pytest.mark.parametrize("random_seed", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_connect_cleans_up_empty_topics(brokers):
    broker = brokers[0]
    topic = "test"

    async def recv():
        yield {"metadata": {"topic": topic}}

    broker.gossip.recv = recv

    handler = broker.subscribe(topic, MagicMock())
    assert topic in broker._handlers
    await broker.unsubscribe(handler)
    assert topic in broker._handlers
    assert len(broker._handlers[topic]) == 0

    await broker.listen()
    assert topic not in broker._handlers
    await broker.close()


@pytest.mark.parametrize("random_seed", [0])
@pytest.mark.parametrize("instances", [1])
@pytest.mark.asyncio
async def test_wildcard_topic(brokers):
    broker = brokers[0]
    topic = "test.*"

    async def recv():
        yield {"metadata": {"topic": "test.1"}}
        yield {"metadata": {"topic": "test.2"}}

    broker.gossip.recv = recv

    handler = MagicMock()
    handler = broker.subscribe(topic, handler)
    handler.chan.send = AsyncMagicMock()

    await broker.listen()
    assert handler.chan.send.call_count == 2
    await broker.close()


@pytest.mark.parametrize("random_seed", [0])
@pytest.mark.parametrize("instances", [2])
@pytest.mark.asyncio
async def test_publish_to_specific_nodes(brokers):
    pub = brokers[0]
    pub.gossip.send = AsyncMagicMock()
    sub = brokers[1]
    pub.gossip.topology.add([sub.gossip.topology.node])

    topic = "test"
    message = {"metadata": {}}

    pub.gossip.send.reset_mock()
    await pub.publish(topic, message, [sub.gossip.topology.node_id])
    pub.gossip.send.assert_called_once_with(message, sub.gossip.topology.node_id)

    await pub.close()
    await sub.close()
