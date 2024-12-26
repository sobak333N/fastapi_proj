from typing import Coroutine
import asyncio


class TaskManager:
    tasks = set()

    @classmethod
    async def create_task(cls, coro: Coroutine) -> None:
        task = asyncio.create_task(coro)
        cls.tasks.add(task)
        task.add_done_callback(cls.tasks.discard)
        return task

    @classmethod
    async def wait_for_end(cls):
        if cls.tasks:
            await asyncio.gather(*cls.tasks)