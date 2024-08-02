import warnings
from datetime import datetime, timezone as dtimezone
from typing import Any, Callable, Dict, Type, Union

from asyncz.schedulers import AsyncIOScheduler
from asyncz.schedulers.types import SchedulerType
from asyncz.triggers.types import TriggerType
from asyncz.typing import Undefined, undefined

from esmerald.conf import settings
from esmerald.contrib.schedulers.base import SchedulerConfig
from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.module_loading import import_string

SchedulerCallable = Callable[..., Any]


class AsynczConfig(SchedulerConfig):
    """
    Implements an integration with Asyncz, allowing to
    customise the scheduler with the provided configurations.
    """

    def __init__(
        self,
        scheduler_class: Type[SchedulerType] = AsyncIOScheduler,
        tasks: Union[Dict[str, str]] = None,
        timezone: Union[dtimezone, str, None] = None,
        configurations: Union[Dict[str, Dict[str, str]], None] = None,
        **kwargs: Dict[str, Any],
    ):
        """
        Initializes the AsynczConfig object.

        Args:
            scheduler_class: The class of the scheduler to be used.
            tasks: A dictionary of tasks to be registered in the scheduler.
            timezone: The timezone to be used by the scheduler.
            configurations: Extra configurations to be passed to the scheduler.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.scheduler_class = scheduler_class
        self.tasks = tasks
        self.timezone = timezone
        self.configurations = configurations
        self.options = kwargs

        for task, module in self.tasks.items():
            if not isinstance(task, str) or not isinstance(module, str):
                raise ImproperlyConfigured("The dict of tasks must be Dict[str, str].")

        if not self.tasks:
            warnings.warn(
                "Esmerald is starting the scheduler, yet there are no tasks declared.",
                UserWarning,
                stacklevel=2,
            )

        # Load the scheduler object
        self.handler = self.get_scheduler(
            scheduler=self.scheduler_class,
            timezone=self.timezone,
            configurations=self.configurations,
            **self.options,
        )

        self.register_tasks(tasks=self.tasks)

    def register_tasks(self, tasks: Dict[str, str]) -> None:
        """
        Registers the tasks in the Scheduler.

        Args:
            tasks: A dictionary of tasks to be registered in the scheduler.
        """
        for task, _module in tasks.items():
            imported_task = f"{_module}.{task}"
            scheduled_task: "Task" = import_string(imported_task)

            if not scheduled_task.is_enabled:
                continue

            try:
                scheduled_task.add_task(self.handler)
            except Exception as e:
                raise ImproperlyConfigured(str(e)) from e

    def get_scheduler(
        self,
        scheduler: Type[SchedulerType],
        timezone: Union[dtimezone, str, None] = None,
        configurations: Union[Dict[str, Any], None] = None,
        **options: Dict[str, Any],
    ) -> SchedulerType:
        """
        Initiates the scheduler from the given time.
        If no value is provided, it will default to AsyncIOScheduler.

        The value of `scheduler_class` can be overwritten by any esmerald custom settings.

        Args:
            scheduler: The class of the scheduler to be used.
            timezone: The timezone instance.
            configurations: A dictionary with extra configurations to be passed to the scheduler.
            **options: Additional options.

        Returns:
            SchedulerType: An instance of a Scheduler.
        """
        if not timezone:
            timezone = settings.timezone

        if not configurations:
            return scheduler(timezone=timezone, **options)  # type: ignore

        return scheduler(global_config=configurations, timezone=timezone, **options)  # type: ignore

    async def start(self, **kwargs: Any) -> None:
        """
        Starts the scheduler.

        Args:
            **kwargs: Additional keyword arguments.
        """
        self.handler.start(**kwargs)

    async def shutdown(self, **kwargs: Any) -> None:
        """
        Shuts down the scheduler.

        Args:
            **kwargs: Additional keyword arguments.
        """
        self.handler.shutdown(**kwargs)


class Task:
    """
    Base for the scheduler decorator that will auto discover the
    tasks in the application and add them to the internal scheduler.
    """

    def __init__(
        self,
        fn: Any = None,
        *,
        name: Union[str, None] = None,
        trigger: Union[TriggerType, None] = None,
        id: Union[str, None] = None,
        mistrigger_grace_time: Union[int, Undefined, None] = undefined,
        coalesce: Union[bool, Undefined] = undefined,
        max_instances: Union[int, Undefined, None] = undefined,
        next_run_time: Union[datetime, str, Undefined, None] = undefined,
        store: Union[str, None] = None,
        executor: Union[str, None] = None,
        replace_existing: bool = False,
        args: Union[Any, None] = None,
        kwargs: Union[Dict[str, Any], None] = None,
        is_enabled: bool = True,
    ) -> None:
        """
        Initializes a new instance of the `Task` class for the  Scheduler.

        Args:
            name (str, optional): Textual description of the task.
            trigger (TriggerType, optional): An instance of a trigger class.
            id (str, optional): Explicit identifier for the task.
            mistrigger_grace_time (int, optional): Seconds after the designated runtime that the task is still allowed to be run
                (or None to allow the task to run no matter how late it is).
            coalesce (bool, optional): Run once instead of many times if the scheduler determines that the task should be run more than once in succession.
            max_instances (int, optional): Maximum number of concurrently running instances allowed for this task.
            next_run_time (datetime, optional): When to first run the task, regardless of the trigger (pass None to add the task as paused).
            store (str, optional): Alias of the task store to store the task in.
            executor (str, optional): Alias of the executor to run the task with.
            replace_existing (bool, optional): True to replace an existing task with the same id
                (but retain the number of runs from the existing one).
            args (Any, optional): List of positional arguments to call func with.
            kwargs (Dict[str, Any], optional): Dict of keyword arguments to call func with.
            is_enabled (bool, optional): True if the task is to be added to the scheduler.
        """
        self.name = name
        self.trigger = trigger
        self.id = id
        self.mistrigger_grace_time = mistrigger_grace_time
        self.coalesce = coalesce
        self.max_instances = max_instances
        self.next_run_time = next_run_time
        self.store = store
        self.executor = executor
        self.replace_existing = replace_existing
        self.args = args
        self.kwargs = kwargs
        self.is_enabled = is_enabled
        self.fn = fn

    def add_task(self, scheduler: SchedulerType) -> None:
        try:
            scheduler.add_task(
                self.fn,
                trigger=self.trigger,
                args=self.args,
                kwargs=self.kwargs,
                id=self.id,
                name=self.name,
                mistrigger_grace_time=self.mistrigger_grace_time,
                coalesce=self.coalesce,
                max_instances=self.max_instances,
                next_run_time=self.next_run_time,
                store=self.store,
                executor=self.executor,
                replace_existing=self.replace_existing,
            )
        except Exception as e:
            raise ImproperlyConfigured(str(e)) from e
