from datetime import datetime
from typing import Optional, Generator

from .base import BaseStorage
from indecro.api.job import Job


class MemoryStorage(BaseStorage):
    def __init__(self):
        self.jobs: set[Job] = set()

    def add_job(self, job: Job):
        self.jobs.add(job)

    def remove_job(self, job: Job):
        self.jobs.remove(job)

    def iter_jobs(
            self,
            *,
            after: Optional[datetime] = None,
            before: Optional[datetime] = None,
            limit: Optional[int] = None
    ) -> Generator[Job, None, None]:

        a = 0
        for job in sorted(self.jobs, key=lambda job: job.next_run_time):

            if job.next_run_time is None:
                if job.rule.get_must_be_scheduled_now_flag():
                    yield job
                    a += 1
            elif (
                    (after is not None and job.next_run_time > after) or
                    (before is not None and job.next_run_time < before)
            ) and \
                    (limit is None or a <= limit):
                yield job
                a += 1
