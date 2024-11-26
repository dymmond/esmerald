from functools import partial
from typing import Any, cast

import orjson

from esmerald.encoders import LILYA_ENCODER_TYPES, json_encoder
from esmerald.responses.json import BaseJSONResponse

try:
    import ujson
except ImportError:  # pragma: no cover
    ujson = None


class ORJSONResponse(BaseJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `ORJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        encoders = (
            (
                (
                    *self.encoders,
                    *LILYA_ENCODER_TYPES.get(),
                )
            )
            if self.encoders
            else None
        )
        return cast(
            bytes,
            json_encoder(
                content,
                json_encode_fn=partial(
                    orjson.dumps, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS
                ),
                post_transform_fn=None,
                with_encoders=encoders,
            ),
        )


class UJSONResponse(BaseJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `UJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        assert ujson is not None, "You must install the encoders or ujson to use UJSONResponse"
        # UJSON is actually in maintainance mode, recommends switch to ORJSON
        # https://github.com/ultrajson/ultrajson
        return ujson.dumps(content, ensure_ascii=False).encode("utf-8")


__all__ = ["ORJSONResponse", "UJSONResponse"]
