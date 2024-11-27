from __future__ import annotations

from inspect import isclass
from typing import Any, Generic, TypeVar, get_args

import msgspec
from lilya._internal._encoders import json_encoder as json_encoder  # noqa
from lilya._utils import is_class_and_subclass
from lilya.encoders import (
    ENCODER_TYPES as LILYA_ENCODER_TYPES,  # noqa
    Encoder as LilyaEncoder,  # noqa
    EncoderProtocol,
    register_encoder as register_encoder,  # noqa
)
from msgspec import Struct
from pydantic import BaseModel
from pydantic_core import PydanticSerializationError

from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.helpers import is_union

T = TypeVar("T")

ENCODER_TYPES = LILYA_ENCODER_TYPES.get()


class Encoder(EncoderProtocol, Generic[T]):
    def is_type(self, value: Any) -> bool:
        """
        Function that checks if the function is
        an instance of a given type (and also for the subclass of the type in case of encode)
        """
        raise NotImplementedError("All Esmerald encoders must implement is_type() method.")

    def is_type_structure(self, value: Any) -> bool:
        """Prevent lilya picking it up for apply_structure."""
        return False

    def serialize(self, obj: Any) -> Any:
        """
        Function that transforms a data structure into a serializable
        object.
        """
        raise NotImplementedError("All Esmerald encoders must implement serialize() method.")

    def encode(self, annotation: Any, value: Any) -> Any:
        """
        Function that transforms the kwargs into a structure
        """
        raise NotImplementedError("All Esmerald encoders must implement encode() method.")


def register_esmerald_encoder(encoder: Encoder | type[Encoder]) -> None:
    """
    Registers an esmerald encoder into available Lilya encoders
    """
    encoder_type = encoder if isclass(encoder) else type(encoder)
    if not isinstance(encoder, Encoder) and not is_class_and_subclass(encoder, Encoder):
        raise ImproperlyConfigured(f"{encoder_type} must be a subclass of Encoder")

    encoder_types = {_encoder.__class__.__name__ for _encoder in LILYA_ENCODER_TYPES.get()}
    if encoder_type.__name__ not in encoder_types:
        register_encoder(encoder)


class MsgSpecEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, Struct) or is_class_and_subclass(value, Struct)

    def serialize(self, obj: Any) -> Any:
        """
        When a `msgspec.Struct` is serialised,
        it will call this function.
        """
        return msgspec.json.decode(msgspec.json.encode(obj))

    def encode(self, annotation: Any, value: Any) -> Any:
        return msgspec.json.decode(msgspec.json.encode(value), type=annotation)


class PydanticEncoder(Encoder):
    def is_type(self, value: Any) -> bool:
        return isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel)

    def serialize(self, obj: BaseModel) -> dict[str, Any]:
        try:
            return obj.model_dump(mode="json")
        except PydanticSerializationError:
            return obj.model_dump()

    def encode(self, annotation: Any, value: Any) -> Any:
        if isinstance(value, BaseModel) or is_class_and_subclass(value, BaseModel):
            return value
        return annotation(**value)


def is_body_encoder(value: Any) -> bool:
    """
    Function that checks if the value is a body encoder.
    """
    encoder_types = LILYA_ENCODER_TYPES.get()
    if not is_union(value):
        return any(encoder.is_type(value) for encoder in encoder_types)

    union_arguments = get_args(value)
    if not union_arguments:
        return False
    return any(
        any(encoder.is_type(argument) for encoder in encoder_types) for argument in union_arguments
    )
