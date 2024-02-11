import asyncio


class Peer:
    def __init__(self, host: str = "0.0.0.0", port: int = 0, loop: asyncio.AbstractEventLoop = None):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

    async def _run(self):
        pass

    def run(self):
        self.loop.run_until_complete(self._run())
