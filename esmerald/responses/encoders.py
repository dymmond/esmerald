from typing import Any

from lilya.responses import JSONResponse as JSONResponse

from esmerald.responses.json import BaseJSONResponse

try:
    import orjson
    from orjson import OPT_OMIT_MICROSECONDS, OPT_SERIALIZE_NUMPY
except ImportError:  # pragma: no cover
    orjson = None

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
        assert orjson is not None, "You must install the encoders or orjson to use ORJSONResponse"
        return orjson.dumps(
            content,
            default=self.transform,
            option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
        )


class UJSONResponse(BaseJSONResponse):
    """
    An alternative to `JSONResponse` and performance wise, faster.

    In the same way the JSONResponse is used, so is the `UJSONResponse`.
    """

    def make_response(self, content: Any) -> bytes:
        assert ujson is not None, "You must install the encoders or ujson to use UJSONResponse"
        return ujson.dumps(content, ensure_ascii=False).encode("utf-8")
