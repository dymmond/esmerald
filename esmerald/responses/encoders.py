from typing import Any

import orjson

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
        return orjson.dumps(
            content,
            default=self.transform,
            option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS,
        )


class UJSONResponse(BaseJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `UJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        assert ujson is not None, "You must install the encoders or ujson to use UJSONResponse"
        return ujson.dumps(content, ensure_ascii=False).encode("utf-8")


__all__ = ["ORJSONResponse", "UJSONResponse"]
