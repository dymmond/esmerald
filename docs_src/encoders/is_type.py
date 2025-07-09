from __future__ import annotations

from typing import Any

from msgspec import Struct
from pydantic import BaseModel

from esmerald.encoders import Encoder
from lilya._utils import is_class_and_subclass


class MsgSpecEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, Struct) or is_class_and_subclass(value, Struct)


class PydanticEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel)
