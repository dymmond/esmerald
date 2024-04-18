from __future__ import annotations

from typing import Any

import msgspec
from lilya._internal._encoders import json_encoder as json_encoder  # noqa
from lilya._utils import is_class_and_subclass
from lilya.encoders import (
    ENCODER_TYPES as ENCODER_TYPES,  # noqa
    Encoder as Encoder,  # noqa
    register_encoder as register_encoder,  # noqa
)
from msgspec import Struct
from pydantic import BaseModel

from esmerald.exceptions import ImproperlyConfigured


class MsgSpecEncoder(Encoder):
    __type__ = Struct

    def serialize(self, obj: Any) -> Any:
        """
        When a `msgspec.Struct` is serialised,
        it will call this function.
        """
        return msgspec.json.decode(msgspec.json.encode(obj), type=obj.__class__)


class PydanticEncoder(Encoder):
    __type__ = BaseModel

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        return obj.model_dump()


def register_esmerald_encoder(encoder: Encoder[Any]) -> None:
    if not isinstance(encoder, Encoder) and not is_class_and_subclass(encoder, Encoder):  # type: ignore
        raise ImproperlyConfigured(f"{type(encoder)} must be a subclass of Encoder")
    register_encoder(encoder)
