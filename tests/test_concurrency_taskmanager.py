import asyncio

import pytest

from aiogossip.concurrency.taskmanager import TaskManager


@pytest.mark.asyncio
async def test_create_task():
    async def coro():
        await asyncio.sleep(0.02)
        return True

    task_manager = TaskManager()
    task = task_manager.create_task(coro())

    assert not task.done()
    await asyncio.sleep(0.03)
    assert task.done()
    assert task.result() is True


@pytest.mark.asyncio
async def test_close():
    async def coro():
        await asyncio.sleep(0.02)
        return True

    task_manager = TaskManager()
    task_manager.create_task(coro())
    task_manager.create_task(coro())
    task_manager.create_task(coro())

    assert len(task_manager.tasks) == 3
    assert len(task_manager.named_tasks) == 0

    await task_manager.close()

    assert len(task_manager.tasks) == 0
    assert len(task_manager.named_tasks) == 0


@pytest.mark.asyncio
async def test_named_task():
    async def coro():
        await asyncio.sleep(0.02)
        return True

    task_manager = TaskManager()
    task_manager.create_task(coro(), name="task1")
    task_manager.create_task(coro(), name="task2")

    assert "task1" in task_manager.named_tasks
    assert "task2" in task_manager.named_tasks

    task1 = task_manager["task1"]
    task2 = task_manager["task2"]

    assert not task1.done()
    assert not task2.done()

    await asyncio.sleep(0.03)

    assert task1.done()
    assert task2.done()
    assert task1.result() is True
    assert task2.result() is True
