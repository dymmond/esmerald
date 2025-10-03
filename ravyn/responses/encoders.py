from functools import partial
from typing import Any

import orjson
from lilya.responses import RESPONSE_TRANSFORM_KWARGS

from .json import BaseJSONResponse
from .mixins import ORJSONTransformMixin

try:
    import ujson
except ImportError:  # pragma: no cover
    ujson = None


class ORJSONResponse(ORJSONTransformMixin, BaseJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `ORJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        new_params = RESPONSE_TRANSFORM_KWARGS.get()
        if new_params:
            new_params = new_params.copy()
        else:
            new_params = {}
        new_params.setdefault(
            "json_encode_fn",
            partial(
                orjson.dumps,
                option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS,
            ),
        )
        with self.with_transform_kwargs(new_params):
            return super().make_response(content)


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
