import asyncio


def print_exception(task):
    try:
        e = task.exception()
    except asyncio.CancelledError:
        return

    if not e:
        return

    task.print_stack()
