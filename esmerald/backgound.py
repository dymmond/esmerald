from typing import Any, Callable, List, Optional, TypeVar

from starlette.background import BackgroundTask as StarletteBackgroundTask  # noqa
from starlette.background import BackgroundTasks as StarletteBackgroundTasks  # noqa
from starlette.responses import Response as StarletteResponse  # noqa
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R", bound=StarletteResponse)


class BackgroundTask(StarletteBackgroundTask):
    def __init__(self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs) -> None:
        super().__init__(func, *args, **kwargs)


class BackgroundTasks(StarletteBackgroundTasks):
    def __init__(self, tasks: Optional[List[BackgroundTask]] = None):
        super().__init__(tasks=tasks)
