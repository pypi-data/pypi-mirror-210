from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from indecro.api.job import Job
from indecro.api.rules import Rule


# TODO: Add an repr for all exceptions


class RuleException(Exception):
    def __init__(self, rule: Rule):
        self.rule = rule

        super().__init__()


class SchedulerException(Exception):
    if TYPE_CHECKING:
        def __init__(self, job: Job):
            self.job = job


class RuleCannotSmthException(RuleException):
    def __init__(self, *, after: datetime, by_rule: Rule):
        super().__init__(rule=by_rule)

        self.after = after
        self.by_rule = by_rule

    def __repr__(self):
        return f'{self.__class__.__name__}(after={self.after}, by_rule={self.by_rule})'


class CannotPredictJobSchedulingTime(RuleCannotSmthException):
    pass


class JobNeverBeScheduled(RuleCannotSmthException):
    pass
