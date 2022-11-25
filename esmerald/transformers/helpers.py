from inspect import isclass
from typing import Any, Type, Union

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
from typing_extensions import TypeGuard


def is_pydantic_constrained_field(
    value: Any,
) -> TypeGuard[
    Union[
        Type[ConstrainedBytes],
        Type[ConstrainedDate],
        Type[ConstrainedDecimal],
        Type[ConstrainedFloat],
        Type[ConstrainedFrozenSet],
        Type[ConstrainedInt],
        Type[ConstrainedList],
        Type[ConstrainedSet],
        Type[ConstrainedStr],
    ]
]:
    return isclass(value) and any(
        issubclass(value, c)
        for c in (
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
