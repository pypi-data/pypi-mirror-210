import asyncio
import functools
from typing import Awaitable, Any, Union, Coroutine, Callable

from indecro.api.executor import Executor as ExecutorProtocol
from indecro.api.job import Job, RunAs


class Executor(ExecutorProtocol):
    def __init__(self):
        self.daemonized_tasks: set[asyncio.Task] = set()

    async def execute(self, job: Job):
        if job.is_running:
            return False

        if job.daemonize is RunAs.FUNCTION:
            res = self.sync_worker(job.task, job)

            if isinstance(res, Awaitable):
                await res

        else:
            if job.daemonize is RunAs.THREAD:
                res = asyncio.to_thread(functools.partial(self.sync_worker, job.task, job))
            elif job.daemonize is RunAs.ASYNC_TASK:
                res = job.task()

                if not isinstance(res, Awaitable):
                    pass
                    # TODO: Create warning message here
            else:
                raise ValueError(f'Invalid job.daemonize value: {job.daemonize}')

            if isinstance(res, Coroutine):
                self.daemonized_tasks.add(task := asyncio.create_task(self.worker_for_awaitable(res, Job)))
                job.running_task = task

        return True

    async def worker_for_awaitable(self, awaitable: Awaitable, job: Job):
        job.is_running = True
        res = await awaitable
        job.is_running = False

        self.daemonized_tasks.remove(job.running_task)

        job.running_task = None

        return res

    @staticmethod
    def sync_worker(target: Callable, job: Job):
        job.is_running = True
        res = target()
        job.is_running = False

        return res
