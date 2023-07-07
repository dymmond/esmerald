from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union

from esmerald.datastructures.base import ResponseContainer

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType

try:
    from esmerald.responses.encoders import ORJSONResponse
except ImportError:
    ORJSONResponse = None  # type: ignore

try:
    from esmerald.responses.encoders import UJSONResponse
except ImportError:
    UJSONResponse = None  # type: ignore


class OrJSON(ResponseContainer[ORJSONResponse]):
    media_type: str = "application/json"
    content: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.status_code = status_code

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> ORJSONResponse:
        assert (
            ORJSONResponse is not None
        ), "You must install the encoders or orjson to use ORJSONResponse"
        status = self.status_code or status_code

        return ORJSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )


class UJSON(ResponseContainer[UJSONResponse]):
    media_type: str = "application/json"
    content: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None

    def __init__(
        self,
        content: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.content = content
        self.status_code = status_code

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> UJSONResponse:
        assert (
            UJSONResponse is not None
        ), "You must install the encoders or ujson to use UJSONResponse"
        status = self.status_code or status_code

        return UJSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )
