from typing import Any, Callable, Type, TypeVar

from pydantic_core import PydanticUndefined

T = TypeVar("T")


class Void:
    """A placeholder class."""


VoidType = Type[Void]
AnyCallable = Callable[..., Any]
Undefined = PydanticUndefined
