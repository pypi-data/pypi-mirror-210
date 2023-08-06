from abc import ABC, abstractmethod
from datetime import datetime

from typing import Generator, AsyncGenerator, Optional, Union

from indecro.api.job import Job
from indecro.api.storage import Storage, AsyncStorage


class BaseStorage(Storage, ABC):
    def get_closest_job(self, *, after: datetime) -> Union[Job, None]:
        for job in self.iter_jobs(after=after):
            return job
        return None

    def get_duty_job(self, *, before: datetime) -> Union[Job, None]:
        for job in self.iter_jobs(before=before):
            return job
        return None

    @property
    def duty_job(self) -> Union[Job, None]:
        return self.get_duty_job(before=datetime.now())

    @property
    def next_job(self) -> Union[Job, None]:
        return self.get_closest_job(after=datetime.now())

    @abstractmethod
    def iter_jobs(
            self,
            *,
            after: Optional[datetime] = None,
            before: Optional[datetime] = None,
            limit: Optional[int] = None
    ) -> Generator[Job, None, None]:
        raise NotImplementedError()


class BaseAsyncStorage(AsyncStorage, ABC):
    async def get_closest_job(self, *, after: datetime) -> Union[Job, None]:
        async for job in self.iter_jobs(after=after):
            return job
        return None

    async def get_duty_job(self, *, before: datetime) -> Union[Job, None]:
        async for job in self.iter_jobs(before=before):
            return job
        return None

    @property
    async def duty_job(self) -> Union[Job, None]:
        return await self.get_duty_job(before=datetime.now())

    @property
    async def next_job(self) -> Union[Job, None]:
        return await self.get_closest_job(after=datetime.now())

    @abstractmethod
    async def iter_jobs(
            self,
            *,
            after: Optional[datetime] = None,
            before: Optional[datetime] = None,
            limit: Optional[int] = None
    ) -> AsyncGenerator[Job, None]:
        raise NotImplementedError()
        yield  # For generator-like typehints in PyCharm


__all__ = ('BaseStorage', 'BaseAsyncStorage')
