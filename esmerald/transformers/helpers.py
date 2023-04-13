import inspect
from typing import Any

from pydantic import (
    ConstrainedBytes,
    ConstrainedDate,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedFrozenSet,
    ConstrainedInt,
    ConstrainedList,
    ConstrainedSet,
    ConstrainedStr,
)

from esmerald.transformers.types import ConstrainedField


def is_pydantic_constrained_field(value: Any) -> ConstrainedField:
    return inspect.isclass(value) and any(
        issubclass(value, _type)
        for _type in (
            ConstrainedBytes,
            ConstrainedDate,
            ConstrainedDecimal,
            ConstrainedFloat,
            ConstrainedFrozenSet,
            ConstrainedInt,
            ConstrainedList,
            ConstrainedSet,
            ConstrainedStr,
        )
    )
