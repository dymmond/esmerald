from json import dumps
from typing import TYPE_CHECKING, Any, Dict, Generic, NoReturn, Optional, TypeVar, Union, cast

from pydantic import BaseModel
from starlette import status
from starlette.responses import FileResponse as FileResponse  # noqa
from starlette.responses import HTMLResponse as HTMLResponse  # noqa
from starlette.responses import JSONResponse as JSONResponse  # noqa
from starlette.responses import PlainTextResponse as PlainTextResponse  # noqa
from starlette.responses import RedirectResponse as RedirectResponse  # noqa
from starlette.responses import Response as StarletteResponse  # noqa
from starlette.responses import StreamingResponse as StreamingResponse  # noqa

from esmerald.enums import MediaType
from esmerald.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from esmerald.backgound import BackgroundTask, BackgroundTasks
    from esmerald.types import ResponseCookies

T = TypeVar("T")


class Response(StarletteResponse, Generic[T]):
    def __init__(
        self,
        content: T,
        *,
        status_code: Optional[int] = status.HTTP_200_OK,
        media_type: Optional[Union["MediaType", str]] = MediaType.JSON,
        background: Optional[Union["BackgroundTask", "BackgroundTasks"]] = None,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional["ResponseCookies"] = None,
    ) -> None:
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers or {},
            media_type=media_type,
            background=cast("BackgroundTask", background),
        )
        self.cookies = cookies or []

    @staticmethod
    def transform(value: Any) -> Dict[str, Any]:
        if isinstance(value, BaseModel):
            return value.dict()
        raise TypeError("unsupported type")  # pragma: no cover

    def render(self, content: Any) -> bytes:
        try:
            if (
                content is None
                or content is NoReturn
                and (
                    self.status_code < 100
                    or self.status_code
                    in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
                )
            ):
                return b""
            if self.media_type == MediaType.JSON:
                return dumps(content, default=self.transform, ensure_ascii=False).encode("utf-8")
            return super().render(content)
        except (AttributeError, ValueError, TypeError) as e:
            raise ImproperlyConfigured("Unable to serialize response content") from e
