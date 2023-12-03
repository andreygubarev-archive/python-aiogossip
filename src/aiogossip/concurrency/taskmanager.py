import asyncio


class TaskManager:
    """
    A class that manages asyncio tasks.
    """

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        self.tasks = []
        self.named_tasks = {}

    def create_task(self, coro, name=None):
        """
        Create a task for the given coroutine.

        Args:
            coro: The coroutine to be executed as a task.
            name: Optional name for the task.

        Returns:
            The created task.

        """
        task = self.loop.create_task(coro)
        task.add_done_callback(self._on_done)
        self.tasks.append(task)
        if name:
            self.named_tasks[name] = task
        return task

    def _on_done(self, task):
        self.tasks.remove(task)
        for name, t in self.named_tasks.items():
            if t == task:
                del self.named_tasks[name]
                break

        try:
            exception = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return

        if not exception:
            return

        task.print_stack()

    async def close(self):
        for task in self.tasks:
            task.cancel()
        self.tasks = []
        self.named_tasks = {}

        await asyncio.gather(*self.tasks, return_exceptions=True)

    def __getitem__(self, item):
        return self.named_tasks[item]
