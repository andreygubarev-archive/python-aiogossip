import asyncio
import collections


class Channel:
    """A simple asynchronous channel for sending and receiving messages.

    This class represents a channel that allows sending and receiving messages asynchronously.
    Messages can be sent using the `send` method, and received using the `recv` method.
    If the channel is empty, the `recv` method will wait until a message is sent.

    """

    def __init__(self, loop: asyncio.AbstractEventLoop):
        """Initialize the channel with empty queue and waiters.

        Args:
            loop (asyncio.AbstractEventLoop): The event loop to associate with the channel.

        """
        self._loop = loop

        self._queue = collections.deque()
        self._waiters = collections.deque()

    async def close(self):
        """Close the channel. Any pending waiters are cancelled."""
        for waiter in self._waiters:
            waiter.cancel()
        self._waiters.clear()
        self._queue.clear()

    async def send(self, message):
        """Send a message to the channel. If there are any waiters, wake one up.

        Args:
            message: The message to send.

        """
        self._queue.append(message)
        if self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)

    async def recv(self):
        """Receive a message from the channel. If the channel is empty, wait until a message is sent.

        Returns:
            The received message.

        """
        while not self._queue:
            waiter = self._loop.create_future()
            self._waiters.append(waiter)
            try:
                await waiter
            except asyncio.CancelledError:
                if waiter in self._waiters:
                    self._waiters.remove(waiter)
                raise
        return self._queue.popleft()
