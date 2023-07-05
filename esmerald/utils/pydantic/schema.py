from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypeVar, cast

T = TypeVar("T", int, float, Decimal)

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo


def is_field_optional(field: "FieldInfo") -> bool:
    """
    Returns bool True or False for the optional model field.
    """
    allow_none = getattr(field, "allow_none", True)
    return not field.is_required() and not is_any_type(field=field) and allow_none


def is_any_type(field: "FieldInfo") -> bool:
    """
    Checks if the field is of type Any.
    """
    name = cast("Any", getattr(field.annotation, "_name", None))
    return (name is not None and "Any" in name) or field.annotation is Any
