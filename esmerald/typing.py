from typing import Any, Type, TypeVar

T = TypeVar("T")


class Void:
    """A placeholder class."""


class UndefinedType:
    def __repr__(self) -> str:
        return "PydanticUndefined"

    def __copy__(self: T) -> T:
        return self

    def __reduce__(self) -> str:
        return "Undefined"

    def __deepcopy__(self: T, _: Any) -> T:
        return self


VoidType = Type[Void]
AnyCallable = [..., Any]
Undefined = UndefinedType()
