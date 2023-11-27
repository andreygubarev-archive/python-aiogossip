import asyncio
import traceback


def handle_exception(task):
    try:
        e = task.exception()
    except asyncio.CancelledError:
        return

    if not e:
        return

    traceback.print_exception(type(e), e, e.__traceback__)
