from typing import Any, Type, TypeVar

from pydantic_core import PydanticUndefined

T = TypeVar("T")


class Void:
    """A placeholder class."""


VoidType = Type[Void]
AnyCallable = [..., Any]
Undefined = PydanticUndefined
