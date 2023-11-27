import asyncio
from unittest.mock import patch

import pytest

from aiogossip.errors import print_exception


@pytest.mark.asyncio
async def test_print_exception_handles_cancelled_error():
    task = asyncio.create_task(asyncio.sleep(0.1))
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    print_exception(task)


@pytest.mark.asyncio
async def test_print_exception_prints_stack_trace():
    async def raise_exception():
        await asyncio.sleep(0.1)
        raise Exception()

    task = asyncio.create_task(raise_exception())
    task.add_done_callback(print_exception)

    with patch.object(task, "print_stack") as mock_print_stack:
        await asyncio.sleep(0.2)
        mock_print_stack.assert_called_once()
