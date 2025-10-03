from datetime import datetime
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union

from asyncz.triggers.types import TriggerType
from asyncz.typing import Undefined, undefined
from lilya.compat import is_async_callable

from ravyn.contrib.schedulers.asyncz.config import Task

F = TypeVar("F", bound=Callable[..., Union[Awaitable[Any], Any]])


def scheduler(
    *,
    name: Optional[str] = None,
    trigger: Optional[TriggerType] = None,
    id: Optional[str] = None,
    mistrigger_grace_time: Union[int, Undefined, None] = undefined,
    coalesce: Union[bool, Undefined] = undefined,
    max_instances: Union[int, Undefined, None] = undefined,
    next_run_time: Union[datetime, str, Undefined, None] = undefined,
    store: Union[str, None] = None,
    executor: Union[str, None] = None,
    replace_existing: bool = True,
    extra_args: Optional[Any] = None,
    extra_kwargs: Optional[dict[str, Any]] = None,
    is_enabled: bool = True,
) -> Callable[[F], Task]:
    """
    Decorator to schedule a function as a Task with the specified configuration.
    This decorator wraps a function and registers it as a scheduled task, using the provided
    parameters to configure its scheduling behavior. It supports a variety of scheduling options,
    including trigger type, run time, concurrency, and more.

    Parameters:
        name (Optional[str], optional): The name of the scheduled task. Defaults to None.
        trigger (Optional[TriggerType], optional): The trigger that determines when the task runs (e.g., interval, cron). Defaults to None.
        id (Optional[str], optional): Unique identifier for the task. If not provided, one may be generated. Defaults to None.
        mistrigger_grace_time (Union[int, Undefined, None], optional): Time in seconds to allow the job to run after its scheduled time if missed. Defaults to undefined.
        coalesce (Union[bool, Undefined], optional): Whether to coalesce missed runs into a single execution. Defaults to undefined.
        max_instances (Union[int, Undefined, None], optional): Maximum number of concurrent instances allowed for this task. Defaults to undefined.
        next_run_time (Union[datetime, str, Undefined, None], optional): The next scheduled run time for the task. Can be a datetime object or an ISO-formatted string. Defaults to undefined.
        store (Union[str, None], optional): The name of the store to use for persisting the task. Defaults to None.
        executor (Union[str, None], optional): The name of the executor to use for running the task. Defaults to None.
        replace_existing (bool, optional): Whether to replace an existing task with the same ID. Defaults to True.
        extra_args (Optional[Any], optional): Additional positional arguments to pass to the task function. Defaults to None.
        extra_kwargs (Optional[dict[str, Any]], optional): Additional keyword arguments to pass to the task function. Defaults to None.
        is_enabled (bool, optional): Whether the task is enabled and should be scheduled. Defaults to True.

    Returns:
        Callable[[F], Task]: A decorator that, when applied to a function, returns a Task instance
        configured with the provided scheduling options.
    Example:
        @scheduler(trigger="interval", seconds=10, name="my_task")
        async def my_task():
            print("Task executed every 10 seconds")
    """

    def decorator(func: Callable) -> "Task":
        if is_async_callable(func):

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)

        task = Task(
            fn=wrapper,
            name=name,
            trigger=trigger,
            id=id,
            mistrigger_grace_time=mistrigger_grace_time,
            coalesce=coalesce,
            max_instances=max_instances,
            next_run_time=next_run_time,
            store=store,
            executor=executor,
            replace_existing=replace_existing,
            args=extra_args,
            kwargs=extra_kwargs,
            is_enabled=is_enabled,
        )
        return task

    return decorator
