from __future__ import annotations

from typing import Any

from attrs import asdict, define, field, has

from ravyn.encoders import Encoder


class AttrsEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return has(value)

    def serialize(self, obj: Any) -> Any:
        return asdict(obj)

    def encode(self, annotation: Any, value: Any) -> Any:
        return annotation(**value)


# The way an `attr` object is defined
@define
class AttrItem:
    name: str = field()
    age: int = field()
    email: str
