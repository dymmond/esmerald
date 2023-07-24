import dataclasses
from dataclasses import is_dataclass
from typing import Any, Dict

from pydantic import BaseModel

from esmerald.responses import JSONResponse as JSONResponse  # noqa


class BaseJSONResponse(JSONResponse):
    """
    Making sure it parses all the values from pydantic into dictionary.
    """

    @staticmethod
    def transform(value: Any) -> Dict[str, Any]:  # pragma: no cover
        """
        Makes sure that every value is checked and if it's a pydantic model then parses into
        a dict().
        """
        if isinstance(value, BaseModel):
            return value.model_dump()
        if is_dataclass(value):
            return dataclasses.asdict(value)
        raise TypeError("unsupported type")
