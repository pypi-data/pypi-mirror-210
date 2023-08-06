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
            # print(f'{job=}')
            # print(job.next_run_time > datetime.now())
            if (
                    (after is not None and job.next_run_time > after) or
                    (before is not None and job.next_run_time < before)
            ) and \
                    (limit is None or a <= limit):
                yield job
                a += 1
