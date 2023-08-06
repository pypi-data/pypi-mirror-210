import asyncio
import functools
from datetime import datetime
from typing import Optional, Union, Awaitable

from indecro.api.executor import Executor
from indecro.api.job import RunAs
from indecro.api.task import Task
from indecro.exceptions import JobNeverBeScheduled, CannotPredictJobSchedulingTime
from indecro.api.job import Job as JobProtocol
from indecro.job import Job
from indecro.api.rules import Rule
from indecro.api.scheduler import Scheduler as SchedulerProtocol
from indecro.api.storage import Storage, AsyncStorage


class Scheduler(SchedulerProtocol):
    def __init__(self, storage: Union[Storage, AsyncStorage], executor: Executor):
        self.storage = storage
        self.executor = executor

        self.running = False

    def job(
            self,
            rule: Rule,

            daemonize: RunAs = RunAs.FUNCTION,

            name: Optional[str] = None,

            *args,
            **kwargs
    ):
        def decorator(task: Task):
            self.add_job(
                task=task,
                rule=rule,
                daemonize=daemonize,
                name=name,
                *args,
                **kwargs
            )
            return task

        return decorator

    def add_job(
            self,
            task: Task,
            rule: Rule,

            daemonize: RunAs = RunAs.FUNCTION,

            name: Optional[str] = None,
            *args,
            **kwargs
    ) -> JobProtocol:
        if isinstance(task, Job):
            job = task
        else:
            try:
                next_run_time = rule.get_next_schedule_time(after=datetime.now())
            except CannotPredictJobSchedulingTime:
                next_run_time = None
            job = Job(
                task=functools.partial(task, *args, **kwargs),
                rule=rule,
                next_run_time=next_run_time,
                name=name,
                scheduler=self,
                executor=self.executor,
                daemonize=daemonize
            )

        return self.storage.add_job(job)

    def stop(self):
        self.running = False

    async def execute_job(self, job: JobProtocol, reschedule: bool = True):
        job_executed = await self.executor.execute(job)

        if reschedule:
            self.schedule_job(job)

        return job_executed

    @staticmethod
    def schedule_job(job: JobProtocol):
        try:
            job.next_run_time = job.rule.get_next_schedule_time(after=datetime.now())
        except CannotPredictJobSchedulingTime:
            pass
        return None

    def remove_job(self, job: JobProtocol):
        return self.storage.remove_job(job)

    async def run(self):
        self.running = True
        while self.running:
            now = datetime.now()

            any_job_started = False
            for job in self.storage.iter_jobs(before=now):
                try:
                    job_executed = await self.execute_job(job)
                except JobNeverBeScheduled:
                    res = self.storage.remove_job(job)

                    if isinstance(res, Awaitable):
                        await res

                    job_executed = False
                except CannotPredictJobSchedulingTime:  # Looks like BoolRule, we just wait
                    job_executed = False

                any_job_started = job_executed or any_job_started

            await asyncio.sleep(not any_job_started)
