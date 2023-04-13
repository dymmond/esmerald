from typing import Any

from pydantic.fields import FieldInfo

from esmerald.utils.constants import IS_DEPENDENCY, SKIP_VALIDATION


def is_dependency_field(val: Any) -> bool:
    return bool(isinstance(val, FieldInfo) and bool(val.extra.get(IS_DEPENDENCY)))


def should_skip_dependency_validation(val: Any) -> bool:
    return bool(is_dependency_field(val) and val.extra.get(SKIP_VALIDATION))
