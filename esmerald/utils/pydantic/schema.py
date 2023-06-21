from decimal import Decimal
from inspect import isclass
from typing import TYPE_CHECKING, Any, Type, TypeVar, cast

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", int, float, Decimal)

if TYPE_CHECKING:
    from pydantic.fields import ModelField
    from typing_extensions import TypeGuard


def is_optional(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Optional."""
    return (
        model_field.allow_none and not is_any(model_field=model_field) and not model_field.required
    )


def is_pydantic_model(value: Any) -> "TypeGuard[Type[BaseModel]]":
    """A function to determine if a given value is a subclass of BaseModel."""
    try:
        return isclass(value) and issubclass(value, (BaseModel, GenericModel))
    except TypeError:  # pragma: no cover
        # isclass(value) returns True for python 3.9+ typings such as list[str] etc.
        # this raises a TypeError in issubclass, and so we need to handle it.
        return False


def is_union(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Union."""
    field_type_repr = repr(model_field.outer_type_)
    if (
        field_type_repr.startswith("typing.Union[")
        or ("|" in field_type_repr)
        or model_field.discriminator_key
    ):
        return True
    return False


def is_any(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Any."""
    type_name = cast("Any", getattr(model_field.outer_type_, "_name", None))
    return model_field.type_ is Any or (type_name is not None and "Any" in type_name)


def is_field_optional(field: "ModelField") -> bool:
    """
    Returns bool True or False for the optional model field.
    """
    return not field.required and not is_any_type(field=field) and field.allow_none


def is_any_type(field: "ModelField") -> bool:
    """
    Checks if the field is of type Any.
    """
    name = cast("Any", getattr(field.outer_type_, "_name", None))
    return (name is not None and "Any" in name) or field.type_ is Any
