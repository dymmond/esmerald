from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from esmerald.datastructures.base import ResponseContainer  # noqa
from esmerald.responses import JSONResponse  # noqa
from esmerald.responses import ORJSONResponse  # noqa
from esmerald.responses import UJSONResponse  # noqa; noqa

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType


class JSON(ResponseContainer[JSONResponse]):
    """
    Returns a wrapper of a JSONResponse.
    """

    content: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> JSONResponse:
        status = self.status_code or status_code

        return JSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )


class OrJSON(JSON, ResponseContainer[ORJSONResponse]):
    ...


class UJSON(JSON, ResponseContainer[UJSONResponse]):
    ...
