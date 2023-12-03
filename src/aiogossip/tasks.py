import asyncio


class TaskManager:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        self.tasks = []
        self.tasks_names = {}

    def create_task(self, coro, name=None):
        task = self.loop.create_task(coro)
        self.tasks.append(task)
        if name:
            self.tasks_names[name] = task
        return task

    def cancel(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        self.tasks_names = {}

    async def close(self):
        self.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
