from typing import Any, Dict

from orjson import OPT_OMIT_MICROSECONDS  # noqa
from pydantic import BaseModel
from esmerald.responses import JSONResponse as JSONResponse  # noqa

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore


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
