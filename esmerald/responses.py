from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    cast,
)

from esmerald.enums import MediaType
from esmerald.exceptions import ImproperlyConfigured
from orjson import OPT_OMIT_MICROSECONDS  # noqa
from orjson import OPT_SERIALIZE_NUMPY, dumps
from pydantic import BaseModel
from starlette import status
from starlette.responses import FileResponse as FileResponse  # noqa
from starlette.responses import HTMLResponse as HTMLResponse  # noqa
from starlette.responses import JSONResponse as JSONResponse  # noqa
from starlette.responses import PlainTextResponse as PlainTextResponse  # noqa
from starlette.responses import RedirectResponse as RedirectResponse  # noqa
from starlette.responses import Response as StarletteResponse  # noqa
from starlette.responses import StreamingResponse as StreamingResponse  # noqa
from starlette.types import Receive, Scope, Send

if TYPE_CHECKING:
    from esmerald.backgound import BackgroundTask, BackgroundTasks
    from esmerald.protocols.template import TemplateEngineProtocol
    from esmerald.types import ResponseCookies

T = TypeVar("T")

try:
    import orjson
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore

try:
    import ujson
except ImportError:  # pragma: nocover
    ujson = None  # type: ignore


class Response(StarletteResponse, Generic[T]):
    def __init__(
        self,
        content: T,
        *,
        status_code: Optional[int] = status.HTTP_200_OK,
        media_type: Optional[Union["MediaType", str]] = None,
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
                return dumps(
                    content,
                    default=self.transform,
                    option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
                )
            return super().render(content)
        except (AttributeError, ValueError, TypeError) as e:
            raise ImproperlyConfigured("Unable to serialize response content") from e


class BaseJSONResponse(JSONResponse):
    """
    Making sure it parses all the values from pydantic into dictionary.
    """

    @staticmethod
    def transform(value: Any) -> Dict[str, Any]:
        """
        Makes sure that every value is checked and if it's a pydantic model then parses into
        a dict().
        """
        if isinstance(value, BaseModel):
            return value.dict()
        raise TypeError("unsupported type")


class ORJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        return orjson.dumps(
            content,
            default=self.transform,
            option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
        )


class UJSONResponse(BaseJSONResponse):
    def render(self, content: Any) -> bytes:
        assert ujson is not None, "ujson must be installed to use UJSONResponse"
        return ujson.dumps(content, ensure_ascii=False, default=self.transform).encode("utf-8")


class TemplateResponse(Response):
    def __init__(
        self,
        template_name: str,
        template_engine: "TemplateEngineProtocol",
        status_code: int = 200,
        context: Optional[Dict[str, Any]] = None,
        background: Optional[Union["BackgroundTask", "BackgroundTasks"]] = None,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional["ResponseCookies"] = None,
    ):
        self.template = template_engine.get_template(template_name)
        self.context = context or {}
        content = self.template.render(**context)
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=MediaType.HTML,
            background=background,
            cookies=cookies,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = self.context.get("request", {})
        extensions = request.get("extensions", {})
        if "http.response.template" in extensions:
            await send(
                {
                    "type": "http.response.template",
                    "template": self.template,
                    "context": self.context,
                }
            )
        await super().__call__(scope, receive, send)
