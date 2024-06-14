from datetime import datetime
from typing import Any, Dict, Optional

from asyncz.triggers.types import TriggerType

from esmerald.contrib.schedulers.asyncz.config import Task


class scheduler(Task):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        trigger: Optional[TriggerType] = None,
        id: Optional[str] = None,
        mistrigger_grace_time: Optional[int] = None,
        coalesce: Optional[bool] = None,
        max_instances: Optional[int] = None,
        next_run_time: Optional[datetime] = None,
        store: Optional[str] = "default",
        executor: Optional[str] = "default",
        replace_existing: bool = True,
        extra_args: Optional[Any] = None,
        extra_kwargs: Optional[Dict[str, Any]] = None,
        is_enabled: bool = True,
    ) -> None:
        super().__init__(
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
