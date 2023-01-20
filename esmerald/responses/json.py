from typing import Any, Dict

from orjson import OPT_OMIT_MICROSECONDS  # noqa
from orjson import OPT_SERIALIZE_NUMPY
from pydantic import BaseModel
from starlette.responses import JSONResponse as JSONResponse  # noqa

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore


class BaseJSONResponse(JSONResponse):
    """
    Making sure it parses all the values from pydantic into dictionary.
    """

    @staticmethod
    def transform(value: Any) -> Dict[str, Any]:
        """
        Makes sure that every value is checked and if it's a pydantic model then parses into
        a dict().
        """
        if isinstance(value, BaseModel):
            return value.dict()
        raise TypeError("unsupported type")


class ORJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content,
            default=self.transform,
            option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
        )


class UJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        assert ujson is not None, "ujson must be installed to use UJSONResponse"
        return ujson.dumps(content, ensure_ascii=False, default=self.transform).encode("utf-8")
