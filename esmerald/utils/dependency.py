from typing import Any

from pydantic.fields import FieldInfo

from esmerald.utils.constants import IS_DEPENDENCY, SKIP_VALIDATION


def is_dependency_field(val: Any) -> bool:
    json_schema_extra = getattr(val, "json_schema_extra", None) or {}
    return bool(isinstance(val, FieldInfo) and bool(json_schema_extra.get(IS_DEPENDENCY)))


def should_skip_dependency_validation(val: Any) -> bool:
    json_schema_extra = getattr(val, "json_schema_extra", None) or {}
    return bool(is_dependency_field(val) and json_schema_extra.get(SKIP_VALIDATION))
