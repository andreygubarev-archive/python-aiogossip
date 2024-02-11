import asyncio

from .address import Address
from .message import Message


class Dispatcher:
    """Dispatches messages to the appropriate handler."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.handlers = set()

    def dispatch(self, msg: Message, addr: Address):
        """Dispatch a message to the appropriate handler."""
        for handler in self.handlers:
            self.loop.create_task(handler(msg, addr))

    def add_handler(self, handler):
        """Add a handler to the dispatcher."""
        self.handlers.add(handler)
