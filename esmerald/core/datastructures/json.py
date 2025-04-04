from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.base import ResponseContainer  # noqa
from esmerald.responses import JSONResponse  # noqa
from esmerald.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class JSON(ResponseContainer[JSONResponse]):
    """
    Returns a wrapper of a JSONResponse.
    """

    content: Annotated[
        Optional[Dict[str, Any]],
        Doc(
            """
            The content being sent to the response.
            """
        ),
    ] = None
    status_code: Annotated[
        Optional[int],
        Doc(
            """
            The status code of the response. It will default to the
            [handler](https://esmerald.dev/routing/handlers/) if none is provided.
            """
        ),
    ] = None
    media_type: Annotated[
        str,
        Doc(
            """
            The media type of the response.
            """
        ),
    ] = "application/json"

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.content = content
        self.status_code = status_code
        self._media_type = self.media_type

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
