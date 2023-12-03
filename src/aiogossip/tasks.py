import asyncio


class TaskManager:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        self.tasks = []

    def create_task(self, coro, name=None):
        task = self.loop.create_task(coro)
        task.add_done_callback(self.on_task_done)
        self.tasks.append(task)
        return task

    def on_task_done(self, task):
        self.tasks.remove(task)

        try:
            exception = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return

        if not exception:
            return

        task.print_stack()

    def cancel(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []

    async def close(self):
        self.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
