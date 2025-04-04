from typing import Any, Union

from esmerald.core.datastructures.json import JSON

try:
    from esmerald.core.datastructures.encoders import UJSON, OrJSON
except ImportError:
    UJSON = Any  # type: ignore[misc,assignment]
    OrJSON = Any  # type: ignore[misc,assignment]

EncoderType = Union[JSON, UJSON, OrJSON]
