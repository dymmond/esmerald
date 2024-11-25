from __future__ import annotations

from typing import Any, get_args

from lilya._internal._encoders import ModelDumpEncoder
from lilya.encoders import (
    ENCODER_TYPES as ENCODER_TYPES_CTX,  # noqa
    Encoder,
    EncoderProtocol,  # noqa
    MoldingProtocol,  # noqa
    json_encode,
    register_encoder,  # noqa
)

from esmerald.exceptions import ImproperlyConfigured
from esmerald.utils.helpers import is_union

ENCODER_TYPES = ENCODER_TYPES_CTX.get()


def register_esmerald_encoder(
    encoder: EncoderProtocol | MoldingProtocol | type[EncoderProtocol] | type[MoldingProtocol],
) -> None:
    """
    Registers an esmerald encoder into available Lilya encoders
    """
    try:
        register_encoder(encoder)
    except RuntimeError:
        raise ImproperlyConfigured(f"{type(encoder)} must be a subclass of Encoder") from None


PydanticEncoder = ModelDumpEncoder
try:
    import msgspec

    class MsgSpecEncoder(Encoder):
        __type__ = msgspec.Struct

        def serialize(self, obj: Any) -> Any:
            """
            When a `msgspec.Struct` is serialised,
            it will call this function.
            """
            return msgspec.json.decode(msgspec.json.encode(obj))

        def encode(self, annotation: Any, value: Any) -> Any:
            return msgspec.json.decode(msgspec.json.encode(value), type=annotation)

    register_esmerald_encoder(MsgSpecEncoder)
except ImportError:
    pass

json_encoder = json_encode


def is_body_encoder(value: Any) -> bool:
    """
    Function that checks if the value is a body encoder.
    """
    encoder_types = ENCODER_TYPES_CTX.get()
    if not is_union(value):
        return any(encoder.is_type(value) for encoder in encoder_types)

    union_arguments = get_args(value)
    if not union_arguments:
        return False
    return any(
        any(encoder.is_type(argument) for encoder in encoder_types) for argument in union_arguments
    )
