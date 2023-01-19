from typing import Any, Callable, Optional

from esmerald import injector


def Injects(  # noqa: N802
    dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True
) -> Any:
    return injector.Inject(dependency=dependency, use_cache=use_cache)
