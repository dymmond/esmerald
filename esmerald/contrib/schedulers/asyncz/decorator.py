from datetime import datetime
from typing import Any, Dict, Optional, Union, cast

from asyncz.triggers.types import TriggerType
from asyncz.typing import Undefined, undefined

from esmerald.contrib.schedulers.asyncz.config import Task


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
    extra_kwargs: Optional[Dict[str, Any]] = None,
    is_enabled: bool = True,
) -> "Task":
    def wrapper(func: Any) -> Task:
        task = Task(
            fn=func,
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

    return cast(Task, wrapper)
