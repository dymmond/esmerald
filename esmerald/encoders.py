from __future__ import annotations

from typing import Any, TypeVar

import msgspec
from lilya._internal._encoders import json_encoder as json_encoder  # noqa
from lilya._utils import is_class_and_subclass
from lilya.encoders import (
    ENCODER_TYPES as ENCODER_TYPES,  # noqa
    Encoder as LilyaEncoder,  # noqa
    register_encoder as register_encoder,  # noqa
)
from msgspec import Struct
from pydantic import BaseModel

from esmerald.exceptions import ImproperlyConfigured

T = TypeVar("T")


class Encoder(LilyaEncoder[T]):

    def is_type(self, value: Any) -> bool:
        """
        Function that checks if the function is
        an instance of a given type
        """
        raise NotImplementedError("All Esmerald encoders must implement is)_type() method")


class MsgSpecEncoder(Encoder):

    def is_type(self, value: Any) -> bool:
        return isinstance(value, Struct) or is_class_and_subclass(value, Struct)

    def serialize(self, obj: Any) -> Any:
        """
        When a `msgspec.Struct` is serialised,
        it will call this function.
        """
        return msgspec.json.decode(msgspec.json.encode(obj))


class PydanticEncoder(Encoder):

    def is_type(self, value: Any) -> bool:
        return isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel)

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        return obj.model_dump()


def register_esmerald_encoder(encoder: Encoder[Any]) -> None:
    if not isinstance(encoder, Encoder) and not is_class_and_subclass(encoder, Encoder):  # type: ignore
        raise ImproperlyConfigured(f"{type(encoder)} must be a subclass of Encoder")

    encoder_types = {encoder.__class__.__name__ for encoder in ENCODER_TYPES}
    if encoder.__name__ not in encoder_types:
        register_encoder(encoder)
