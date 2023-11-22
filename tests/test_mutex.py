import asyncio

import pytest

from aiogossip.mutex import MUTEX, mutex


@pytest.mark.asyncio
async def test_mutex():
    async def func():
        await asyncio.sleep(0.3)
        return True

    mutex_id = "test_mutex"
    assert mutex_id not in MUTEX[func]

    decorated_func = mutex(mutex_id)(func)
    decorated_func_task = asyncio.create_task(decorated_func())
    await asyncio.sleep(0.1)

    assert mutex_id in MUTEX[func]
    assert (await decorated_func()) is None

    await asyncio.sleep(0.1)
    assert (await decorated_func_task) is True
    assert mutex_id not in MUTEX[func]
