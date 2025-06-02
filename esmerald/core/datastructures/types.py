from typing import Any, Union

from esmerald.core.datastructures.json import JSON

try:
    from esmerald.core.datastructures.encoders import UJSON, OrJSON
except ImportError:
    UJSON = Any  # type: ignore[assignment]
    OrJSON = Any  # type: ignore[assignment]

EncoderType = Union[JSON, UJSON, OrJSON]
