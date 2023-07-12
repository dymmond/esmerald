from enum import Enum
from typing import Any, Callable, Dict, Type, TypeVar, Union

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

T = TypeVar("T")


class Void:
    """A placeholder class."""


VoidType = Type[Void]
AnyCallable = Callable[..., Any]
Undefined = PydanticUndefined
ModelMap = Dict[Union[Type[BaseModel], Type[Enum]], str]
