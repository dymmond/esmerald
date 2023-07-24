from decimal import Decimal
from typing import Any, TypeVar, cast

from pydantic.fields import FieldInfo

T = TypeVar("T", int, float, Decimal)


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
