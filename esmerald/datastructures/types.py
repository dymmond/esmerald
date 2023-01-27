from typing import Any, Union

from esmerald.datastructures.json import JSON

try:
    from esmerald.datastructures.encoders import UJSON, OrJSON
except ImportError:
    UJSON = Any
    OrJSON = Any

EncoderType = Union[JSON, UJSON, OrJSON]
