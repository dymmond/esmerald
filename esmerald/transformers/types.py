from typing import Type, Union

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

ConstrainedField = TypeGuard[
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
]
