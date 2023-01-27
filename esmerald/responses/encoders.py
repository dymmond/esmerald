from typing import Any

from starlette.responses import JSONResponse as JSONResponse  # noqa

from esmerald.responses.json import BaseJSONResponse

try:
    import orjson
    from orjson import OPT_OMIT_MICROSECONDS  # noqa
    from orjson import OPT_SERIALIZE_NUMPY
except ImportError:  # pragma: nocover
    raise ImportError(
        "You must install the encoders to use ORJSONResponse and UJSONResponse. You can do it with `pip install esmerald[encoders]`"
    )

try:
    import ujson
except ImportError:  # pragma: nocover
    raise ImportError(
        "You must install the encoders to use ORJSONResponse and UJSONResponse. You can do it with `pip install esmerald[encoders]`"
    )


class ORJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content,
            default=self.transform,
            option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
        )


class UJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        return ujson.dumps(content, ensure_ascii=False, default=self.transform).encode("utf-8")
