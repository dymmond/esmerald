from json import loads
from typing import TYPE_CHECKING, Any, TypeVar, cast

from starlette.requests import ClientDisconnect as ClientDisconnect  # noqa
from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.requests import Request as StarletteRequest  # noqa: F401
from starlette.requests import empty_receive, empty_send  # noqa

from esmerald.exceptions import ImproperlyConfigured
from esmerald.typing import Void

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings
    from esmerald.types import HTTPMethod, Receive, Scope, Send

User = TypeVar("User")


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
    def user(self) -> User:
        if "user" not in self.scope:
            raise ImproperlyConfigured(
                "'user' is not defined in scope, install an AuthMiddleware to set it"
            )
        return cast("User", self.scope["user"])

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

    async def json(self):
        if self._json is Void:
            if "_body" in self.scope:
                body = self.scope["_body"]
            else:
                body = self.scope["_body"] = await self.body() or "null".encode("utf-8")
            self._json = loads(body)
        return self._json
