from typing import Any

from esmerald.utils.constants import EXTRA_KEY_IS_DEPENDENCY, EXTRA_KEY_SKIP_VALIDATION
from pydantic.fields import FieldInfo


def is_dependency_field(val: Any) -> bool:
    return isinstance(val, FieldInfo) and bool(val.extra.get(EXTRA_KEY_IS_DEPENDENCY))


def should_skip_dependency_validation(val: Any) -> bool:
    return is_dependency_field(val) and val.extra.get(EXTRA_KEY_SKIP_VALIDATION)
