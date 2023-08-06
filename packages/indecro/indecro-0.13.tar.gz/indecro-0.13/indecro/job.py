import asyncio
from abc import abstractmethod
from dataclasses import dataclass, is_dataclass
from datetime import datetime
from typing import Optional, Any, Union

from indecro.api.executor import Executor
from indecro.api.task import Task
from indecro.api.rules import Rule, BoolRule
from indecro.api.scheduler import Scheduler
from indecro.api.job import Job as JobProtocol, RunAs


@dataclass
class Job(JobProtocol):  # If the Job is highlighted in red, the bad work of the paycharm with dataclasses and typehints for them is to blame
    task: Task
    rule: Union[Rule, BoolRule]

    next_run_time: datetime

    daemonize: RunAs = RunAs.FUNCTION

    name: Optional[str] = None

    is_running: bool = False

    scheduler: Optional[Scheduler] = None
    executor: Optional[Executor] = None

    running_task: Optional[asyncio.Task] = None

    async def schedule(self, reschedule: bool = True) -> None:
        if self.scheduler is None:
            raise ValueError('To use schedule shortcut you must provide an scheduler attribute for job object')

        await self.scheduler.schedule_job(self)

    async def execute(self, reschedule: bool = True) -> Any:
        if self.executor is None:
            raise ValueError('To use execute shortcut you must provide an executor attribute for job object')

        await self.executor.execute(self)

        if reschedule:
            await self.scheduler.schedule_job(self)

    def __hash__(self):
        return hash(hash(self.rule) + hash(self.name) + hash(self.task))
