import asyncio

import pytest

from aiogossip.mutex import MUTEX, mutex


@pytest.mark.asyncio
async def test_mutex():
    async def func1():
        await asyncio.sleep(0.02)
        return True

    async def func2():
        await asyncio.sleep(0.05)
        return True

    mutex_id = "test_mutex"

    assert mutex_id not in MUTEX[func1]
    assert mutex_id not in MUTEX[func2]

    decorated_func1 = mutex(mutex_id)(func1)
    decorated_func2 = mutex(mutex_id)(func2)

    decorated_func_task1 = asyncio.create_task(decorated_func1())
    decorated_func_task2 = asyncio.create_task(decorated_func2())

    await asyncio.sleep(0.01)

    assert mutex_id in MUTEX[func1]
    assert mutex_id in MUTEX[func2]

    assert (await decorated_func1()) is None
    assert (await decorated_func2()) is None

    await asyncio.sleep(0.02)
    assert (await decorated_func_task1) is True
    assert mutex_id in MUTEX[func1]
    assert mutex_id in MUTEX[func2]

    assert (await decorated_func_task2) is True
