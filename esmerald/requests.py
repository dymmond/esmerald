# from json import loads
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Tuple, cast

from orjson import loads
from starlette.datastructures import URL  # noqa
from starlette.requests import ClientDisconnect as ClientDisconnect  # noqa
from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.requests import Request as StarletteRequest  # noqa: F401
from starlette.requests import empty_receive, empty_send  # noqa
from starlette.types import Receive, Scope, Send

from esmerald.exceptions import InternalServerError
from esmerald.typing import Void
from esmerald.utils.parsers import parse_options_header

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings
    from esmerald.types import HTTPMethod


class Request(StarletteRequest):
    def __init__(
        self,
        scope: Scope,
        receive: Receive = empty_receive,
        send: Send = empty_send,
    ):
        super().__init__(scope, receive, send)
        self.is_connected: bool = True
        self._json: Any = scope.get("_json", Void)
        self._body: Any = scope.get("_body", Void)
        # self._form: Any = scope.get("_form", Void)
        self._content_type: Any = scope.get("_content_type", Void)

    @property
    def app(self) -> "Esmerald":
        return cast("Esmerald", self.scope["app"])

    @property
    def method(self) -> "HTTPMethod":
        return cast("HTTPMethod", self.scope["method"])

    @property
    def global_settings(self) -> Any:
        assert (
            "global_settings" in self.scope
        ), "RequestSettingsMiddleware must be added to the middlewares"
        return cast("EsmeraldAPISettings", self.scope["global_settings"])

    @property
    def app_settings(self) -> Any:
        assert (
            "app_settings" in self.scope
        ), "RequestSettingsMiddleware must be added to the middlewares"
        return cast("EsmeraldAPISettings", self.scope["app_settings"])

    @property
    def content_type(self) -> Tuple[str, Dict[str, str]]:
        if self._content_type is Void:
            self._content_type = self.scope["_content_type"] = parse_options_header(self.headers.get("Content-Type"))  # type: ignore[typeddict-item]
        return cast("Tuple[str, Dict[str, str]]", self._content_type)

    async def json(self) -> Any:
        if self._json is Void:
            self._json = self.scope["_json"] = loads((await self.body()) or b"null")  # type: ignore[typeddict-item]
        return self._json

    async def stream(self) -> AsyncGenerator[bytes, None]:
        if self._body is Void:
            if self.is_connected:
                while event := await self._receive():
                    if event["type"] == "http.request":
                        if event["body"]:
                            yield event["body"]
                        if not event.get("more_body", False):
                            break
                    if event["type"] == "http.disconnect":
                        raise InternalServerError("client disconnected prematurely")

                self.is_connected = False
                yield b""
            else:
                raise InternalServerError("stream consumed")
        else:
            yield self._body
            yield b""
            return

    async def body(self) -> bytes:
        if self._body is Void:
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = self.scope["_body"] = b"".join(chunks)  # type: ignore[typeddict-item]
        return cast("bytes", self._body)

    def url_for(self, __name: str, **path_params: Any) -> Any:
        url: URL = super().url_for(__name, **path_params)
        return str(url)
