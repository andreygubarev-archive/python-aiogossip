import asyncio
import collections


class Channel:
    TIMEOUT = 10

    def __init__(self):
        self._channel = collections.defaultdict(asyncio.Queue)

    async def send(self, key, value):
        chan = self._channel[key]
        await chan.put(value)

    async def recv(self, key, timeout=TIMEOUT):
        chan = self._channel[key]
        async with asyncio.timeout(timeout):
            r = await chan.get()
            chan.task_done()
            return r

    async def close(self, key):
        chan = self._channel[key]
        async with asyncio.timeout(self.TIMEOUT):
            await chan.join()
        self._channel.pop(key, None)

    def __contains__(self, key):
        if key is None:
            return False
        return key in self._channel
