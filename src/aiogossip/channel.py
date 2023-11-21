import asyncio
import collections


class Channel:
    """A simple asynchronous channel for sending and receiving messages."""

    def __init__(self):
        """Initialize the channel with empty queue and waiters."""
        self._queue = collections.deque()
        self._waiters = collections.deque()

    async def send(self, message):
        """Send a message to the channel. If there are any waiters, wake one up."""
        self._queue.append(message)
        if self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)

    async def recv(self):
        """Receive a message from the channel. If the channel is empty, wait until a message is sent."""
        while not self._queue:
            waiter = asyncio.get_running_loop().create_future()
            self._waiters.append(waiter)
            try:
                await waiter
            except asyncio.CancelledError:
                if waiter in self._waiters:
                    self._waiters.remove(waiter)
                raise
        return self._queue.popleft()

    async def close(self):
        """Close the channel. Any pending waiters are cancelled."""
        for waiter in self._waiters:
            waiter.cancel()
        self._waiters.clear()
        self._queue.clear()
