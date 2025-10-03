from __future__ import annotations

from typing import Any

import msgspec
from msgspec import Struct
from pydantic import BaseModel

from ravyn.encoders import Encoder
from lilya._utils import is_class_and_subclass


class MsgSpecEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, Struct) or is_class_and_subclass(value, Struct)

    def serialize(self, obj: Any) -> Any:
        return msgspec.json.decode(msgspec.json.encode(obj))

    def encode(self, annotation: Any, value: Any) -> Any:
        return msgspec.json.decode(msgspec.json.encode(value), type=annotation)


class PydanticEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel)

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        return obj.model_dump()

    def encode(self, annotation: Any, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value
        return annotation(**value)
