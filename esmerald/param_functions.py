from typing import Any, Callable, Optional

from esmerald.params import DirectInject


def DirectInjects(
    dependency: Optional[Callable[..., Any]] = None, *, use_cache: bool = True
) -> Any:
    """
    This function should be only called if not Inject()/Injects is used in the dependencies.
    This is a simple wrapper of the classic Inject()
    """
    return DirectInject(dependency=dependency, use_cache=use_cache)
