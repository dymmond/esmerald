from functools import partial
from inspect import isclass
from typing import Any, cast

import orjson

from esmerald.encoders import ENCODER_TYPES_CTX, json_encode
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

    @staticmethod
    def transform(value: Any, encoders: Any = None) -> dict[str, Any]:
        """
        The transformation of the data being returned.

        Supports all the default encoders from Lilya and custom from Esmerald.
        """
        return cast(
            dict[str, Any],
            json_encode(
                value,
                json_encode_fn=orjson.dumps,
                post_transform_fn=orjson.loads,
                with_encoders=encoders,
            ),
        )

    def make_response(self, content: Any) -> bytes:
        encoders = (
            (
                (
                    *(encoder() if isclass(encoder) else encoder for encoder in self.encoders),
                    *ENCODER_TYPES_CTX.get(),
                )
            )
            if self.encoders
            else None
        )
        return cast(
            bytes,
            json_encode(
                content,
                json_encode_fn=partial(
                    orjson.dumps, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS
                ),
                post_transform_fn=None,
                with_encoders=encoders,
            ),
        )


class UJSONResponse(ORJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `UJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        assert ujson is not None, "You must install the encoders or ujson to use UJSONResponse"
        # UJSON is actually in maintainance mode only, so use mostly orjson
        # https://github.com/ultrajson/ultrajson
        return ujson.dumps(self.transform(content, self.encoders), ensure_ascii=False).encode(
            "utf-8"
        )


__all__ = ["ORJSONResponse", "UJSONResponse"]
