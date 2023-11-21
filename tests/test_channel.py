import asyncio

import pytest

from aiogossip.channel import Channel


@pytest.mark.asyncio
async def test_send_recv():
    channel = Channel()
    await channel.send("message")
    assert await channel.recv() == "message"


@pytest.mark.asyncio
async def test_send_recv_order():
    channel = Channel()
    await channel.send("first")
    await channel.send("second")
    assert await channel.recv() == "first"
    assert await channel.recv() == "second"


@pytest.mark.asyncio
async def test_recv_wait():
    channel = Channel()

    async def send_later():
        await asyncio.sleep(0.1)
        await channel.send("message")

    asyncio.create_task(send_later())
    assert await channel.recv() == "message"


@pytest.mark.asyncio
async def test_close():
    channel = Channel()

    async def recv_later():
        with pytest.raises(asyncio.CancelledError):
            await channel.recv()

    asyncio.create_task(recv_later())
    await asyncio.sleep(0.1)
    await channel.close()


@pytest.mark.asyncio
async def test_cancelled_recv():
    channel = Channel()

    async def cancel_recv():
        await asyncio.sleep(0.1)
        task.cancel()

    task = asyncio.create_task(channel.recv())
    asyncio.create_task(cancel_recv())
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_concurrent_recv():
    channel = Channel()
    await channel.send("first")
    await channel.send("second")

    task1 = asyncio.create_task(channel.recv())
    task2 = asyncio.create_task(channel.recv())

    results = await asyncio.gather(task1, task2)
    assert sorted(results) == ["first", "second"]
