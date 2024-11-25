from __future__ import annotations

from typing import Any

import msgspec
from msgspec import Struct
from pydantic import BaseModel

from esmerald.encoders import Encoder
from lilya._utils import is_class_and_subclass


class MsgSpecEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, Struct)

    def is_type_structure(self, value: Any) -> bool:
        return is_class_and_subclass(value, Struct)

    def serialize(self, obj: Any) -> Any:
        return msgspec.json.decode(msgspec.json.encode(obj))

    def encode(self, annotation: Any, value: Any) -> Any:
        return msgspec.json.decode(msgspec.json.encode(value), type=annotation)


class PydanticEncoder(Encoder):
    # leverage the comfort lilya is_type and is_type_structure defaults
    __type__ = BaseModel

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        return obj.model_dump()

    def encode(self, annotation: Any, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value
        return annotation(**value)
