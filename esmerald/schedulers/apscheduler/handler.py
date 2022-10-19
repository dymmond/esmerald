import warnings
from datetime import datetime
from datetime import timezone as dtimezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from apscheduler.util import undefined
from esmerald.conf import settings
from esmerald.exceptions import ImproperlyConfigured
from esmerald.schedulers.apscheduler.types import TriggerType
from esmerald.types import SchedulerType
from esmerald.utils.module_loading import import_string

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from pydantic.typing import AnyCallable


class Scheduler:
    def __init__(
        self,
        app: Optional["Esmerald"] = None,
        scheduler_class: Optional["SchedulerType"] = None,
        tasks: Optional[Dict[str, str]] = None,
        timezone: Optional[dtimezone] = None,
        configurations: Optional[Dict[str, str]] = None,
    ) -> None:
        self.app = app
        self.tasks = tasks or {}
        self.timezone = timezone
        self.scheduler_class = scheduler_class

        if not self.scheduler_class and self.app.enable_scheduler:
            raise ImproperlyConfigured(
                "It cannot start the scheduler if there is not scheduler_class declared."
            )

        for (
            task,
            module,
        ) in self.tasks.items():
            if not isinstance(task, str) or not isinstance(module, str):
                raise ImproperlyConfigured("The dict of tasks must be Dict[str, str].")

        self.handler = self.get_scheduler(scheduler=self.scheduler_class, timezone=self.timezone)

        if not self.tasks:
            warnings.warn(
                "Esmerald is starting the scheduler, yet there are " "no tasks declared.",
                UserWarning,
                stacklevel=2,
            )

        self.register_events(app=self.app)
        self.register_tasks(tasks=tasks)

    def register_tasks(self, tasks: Dict[str, str]):
        """
        Registers the tasks into the Schedulers
        """
        for task, _module in tasks.items():
            imported_task = f"{_module}.{task}"
            scheduled_task: "Task" = import_string(imported_task)

            if not scheduled_task.is_enabled:
                continue

            try:
                scheduled_task.add_job(self.handler)
            except Exception as e:
                raise ImproperlyConfigured(str(e))

    def register_events(self, app: "Esmerald") -> None:
        """
        Registers the scheduler start/stop events in the application.
        """

        @app.on_event("startup")
        def start_scheduler() -> None:
            self.handler.start()

        @app.on_event("shutdown")
        def stop_scheduler() -> None:
            self.handler.shutdown()

    def get_scheduler(
        self, scheduler: "SchedulerType", timezone: Optional[dtimezone] = None
    ) -> SchedulerType:
        """
        Initiates the scheduler from the given time.
        If no value is provided, it will default to AsyncIOScheduler.

        The value of `scheduler_class` can be overwritten by any custom settings.

        Args:
            scheduler: AsyncIOScheduler

        Return:
            None
        """
        if not timezone:
            timezone = settings.timezone

        return scheduler(timezone=timezone)


class Task:
    """
    Base for the scheduler decorator that will auto discover the
    tasks in the application and add them to the internal scheduler.
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        trigger: Optional[TriggerType] = None,
        identifier: Optional[str] = None,
        misfire_grace_time: Optional[int] = None,
        coalesce: Optional[bool] = None,
        max_intances: Optional[int] = None,
        next_run_time: Optional[datetime] = None,
        jobstore: Optional[str] = "default",
        executor: Optional[str] = "default",
        replace_existing: bool = False,
        args: Optional[Any] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
    ) -> None:
        """_summary_

        Args:
            name (Optional[str], optional): textual description of the job.
            trigger (Optional[TriggerType], optional): an instance of a trigger class.
            identifier (Optional[str], optional): explicit identifier for the job.
            misfire_grace_time (Optional[int], optional): seconds after the designated runtime that the job is still
                allowed to be run (or ``None`` to allow the job to run no matter how late it is).
            coalesce (Optional[bool], optional): run once instead of many times if the scheduler determines that the
                job should be run more than once in succession.
            max_intances (Optional[int], optional): maximum number of concurrently running instances allowed for this
                job.
            next_run_time (Optional[datetime], optional): when to first run the job, regardless of the trigger (pass
                ``None`` to add the job as paused).
            jobstore (Optional[str], optional): alias of the job store to store the job in.
            executor (Optional[str], optional): alias of the executor to run the job with.
            replace_existing (bool, optional): True to replace an existing job with the same ``id``
                (but retain the number of runs from the existing one).
            args (Optional[Any], optional): list of positional arguments to call func with.
            kwargs (Optional[Dict[str, Any]], optional): dict of keyword arguments to call func with.
            is_enabled (bool, optional): True if the the task to be added to the scheduler.
        """
        self.name = name
        self.trigger = trigger
        self.identifier = identifier
        self.misfire_grace_time = misfire_grace_time or undefined
        self.coalesce = coalesce or undefined
        self.max_intances = max_intances or undefined
        self.next_run_time = next_run_time or undefined
        self.jobstore = jobstore
        self.executor = executor
        self.replace_existing = replace_existing
        self.args = args
        self.kwargs = kwargs
        self.is_enabled = is_enabled
        self.fn = None

    def add_job(self, scheduler: "SchedulerType"):
        try:
            scheduler.add_job(
                func=self.fn,
                trigger=self.trigger,
                args=self.args,
                kwargs=self.kwargs,
                id=self.identifier,
                name=self.name,
                misfire_grace_time=self.misfire_grace_time,
                coalesce=self.coalesce,
                max_instances=self.max_intances,
                next_run_time=self.next_run_time,
                jobstore=self.jobstore,
                executor=self.executor,
                replace_existing=self.replace_existing,
            )
        except Exception as e:
            raise ImproperlyConfigured(str(e))

    def __call__(self, fn: "AnyCallable") -> None:
        """Replaces a function with itself."""
        self.fn = fn
        return self


class scheduler(Task):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        trigger: Optional[TriggerType] = None,
        identifier: Optional[str] = None,
        misfire_grace_time: Optional[int] = None,
        coalesce: Optional[bool] = None,
        max_intances: Optional[int] = None,
        next_run_time: Optional[datetime] = None,
        jobstore: Optional[str] = "default",
        executor: Optional[str] = "default",
        replace_existing: bool = True,
        extra_args: Optional[Any] = None,
        extra_kwargs: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
    ) -> None:
        super().__init__(
            name=name,
            trigger=trigger,
            identifier=identifier,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            max_intances=max_intances,
            next_run_time=next_run_time,
            jobstore=jobstore,
            executor=executor,
            replace_existing=replace_existing,
            args=extra_args,
            kwargs=extra_kwargs,
            is_enabled=is_enabled,
        )
