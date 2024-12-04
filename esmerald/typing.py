from typing import Any, Callable, Dict, Set, Type, TypeVar, Union

from pydantic_core import PydanticUndefined

T = TypeVar("T")


class Void:
    """A placeholder class."""


VoidType = Type[Void]
AnyCallable = Callable[..., Any]
Undefined = PydanticUndefined
IncEx = Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any]]
