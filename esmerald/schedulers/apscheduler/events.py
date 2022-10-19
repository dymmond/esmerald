from typing import Any, List, Optional, Union

from apscheduler.events import JobEvent as APSchedulerJobEvent  # noqa
from apscheduler.events import JobExecutionEvent as APSchedulerJobExecutionEvent  # noqa
from apscheduler.events import (
    JobSubmissionEvent as APSchedulerJobSubmissionEvent,
)  # noqa
from apscheduler.events import SchedulerEvent as APSchedulerSchedulerEvent  # noqa

from esmerald.types import DatetimeType  # noqa


class SchedulerEvent(APSchedulerSchedulerEvent):
    """
    An event that concerns the scheduler itself.

    Args:
        code: the type code str of this event.
        alias (optional): alias str of the job store or executor that was added or removed (if applicable).
    """

    def __init__(self, code: str, alias: Optional[str] = None):
        super().__init__(code, alias)


class JobEvent(APSchedulerJobEvent):
    """
    An event that concerns a job.

    Args:
        code: the str type code of this event.
        job_id: identifier of the job in question.
        jobstore: alias str of the job store containing the job in question.
    """

    def __init__(self, code: str, job_id: Union[str, int], jobstore: str):
        super().__init__(code, job_id, jobstore)


class JobSubmissionEvent(APSchedulerJobSubmissionEvent):
    """
    An event that concerns the submission of a job to its executor.

    scheduled_run_times: a list of datetimes when the job was intended to run.
    """

    def __init__(
        self,
        code: str,
        job_id: Union[str, int],
        jobstore: Union[str, int],
        scheduled_run_times: List[DatetimeType],
    ):
        super().__init__(code, job_id, jobstore, scheduled_run_times)


class JobExecutionEvent(APSchedulerJobExecutionEvent):
    """
    An event that concerns the running of a job within its executor.

    scheduled_run_time: the time when the job was scheduled to be run.
    retval: the return value of the successfully executed job.
    exception: the exception raised by the job.
    traceback: a formatted traceback for the exception.
    """

    def __init__(
        self,
        code: str,
        job_id: Union[str, int],
        jobstore: Union[str, int],
        scheduled_run_time: DatetimeType,
        retval: Optional[Any] = None,
        exception: Optional[Any] = None,
        traceback: Optional[Any] = None,
    ):
        super().__init__(code, job_id, jobstore, scheduled_run_time, retval, exception, traceback)
