import asyncio


class Dispatcher:
    """Dispatches messages to the appropriate handler."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
