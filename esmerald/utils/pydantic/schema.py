from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypeVar, cast

T = TypeVar("T", int, float, Decimal)

if TYPE_CHECKING:
    from pydantic_core.core_schema import ModelField


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
