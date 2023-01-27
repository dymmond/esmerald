from typing import TYPE_CHECKING

from esmerald.datastructures.base import ResponseContainer  # noqa
from esmerald.datastructures.json import JSON

if TYPE_CHECKING:
    pass

try:
    from esmerald.responses.encoders import ORJSONResponse, UJSONResponse
except ImportError:
    raise ImportError(
        "You must install the encoders to use URJSON and OrJSON. You can do it with `pip install esmerald[encoders]`"
    )


class OrJSON(JSON, ResponseContainer[ORJSONResponse]):
    ...


class UJSON(JSON, ResponseContainer[UJSONResponse]):
    ...
