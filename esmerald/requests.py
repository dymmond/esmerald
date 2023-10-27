# from json import loads
from typing import TYPE_CHECKING, Any, cast

from orjson import loads
from starlette.datastructures import URL  # noqa
from starlette.requests import ClientDisconnect as ClientDisconnect  # noqa
from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.requests import Request as StarletteRequest  # noqa: F401
from starlette.requests import empty_receive, empty_send  # noqa
from starlette.types import Receive, Scope, Send

from esmerald.typing import Void

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings
    from esmerald.types import HTTPMethod


class Request(StarletteRequest):
    def __init__(
        self,
        scope: "Scope",
        receive: "Receive" = empty_receive,
        send: "Send" = empty_send,
    ):
        super().__init__(scope, receive, send)
        self._json: Any = Void

    @property
    def app(self) -> "Esmerald":
        return cast("Esmerald", self.scope["app"])

    @property
    def method(self) -> "HTTPMethod":
        return cast("HTTPMethod", self.scope["method"])

    @property
    def global_settings(self) -> Any:
        """
        Access to the global settings via `request.global_settings`.
        """
        assert (
            "global_settings" in self.scope
        ), "RequestSettingsMiddleware must be added to the middlewares"
        return cast("EsmeraldAPISettings", self.scope["global_settings"])

    @property
    def app_settings(self) -> Any:
        """
        Access to the app settings via `request.app_settings`.
        """
        assert (
            "app_settings" in self.scope
        ), "RequestSettingsMiddleware must be added to the middlewares"
        return cast("EsmeraldAPISettings", self.scope["app_settings"])

    async def json(self) -> Any:
        if self._json is Void:
            if "_body" in self.scope:
                body = self.scope["_body"]
            else:
                body = self.scope["_body"] = await self.body() or b"null"
            self._json = loads(body)
        return self._json

    def url_for(self, __name: str, **path_params: Any) -> Any:
        url: URL = super().url_for(__name, **path_params)
        return str(url)
