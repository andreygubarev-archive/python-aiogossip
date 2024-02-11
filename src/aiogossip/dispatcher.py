import asyncio

from .address import Address


class Dispatcher:
    """Dispatches messages to the appropriate handler."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.handlers = set()

    def dispatch(self, data: bytes, addr: Address):
        """Dispatch a message to the appropriate handler."""
        for handler in self.handlers:
            self.loop.create_task(handler(data, addr))

    def add_handler(self, handler):
        """Add a handler to the dispatcher."""
        self.handlers.add(handler)
