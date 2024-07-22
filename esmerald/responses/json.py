from typing import Any, Dict, cast

from esmerald.encoders import json_encoder
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
        return cast(Dict[str, Any], json_encoder(value))
