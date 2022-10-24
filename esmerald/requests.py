from typing import TYPE_CHECKING, Any, Dict, TypeVar, cast

from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import parse_query_params
from esmerald.typing import Void
from orjson import loads
from starlette.requests import ClientDisconnect as ClientDisconnect  # noqa
from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.requests import Request as StarletteRequest  # noqa: F401
from starlette.requests import empty_receive, empty_send  # noqa

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.types import HTTPMethod, Receive, Scope, Send

User = TypeVar("User")


class Request(StarletteRequest):
    """Esmerald Request class"""

    def __init__(
        self,
        scope: "Scope",
        receive: "Receive" = empty_receive,
        send: "Send" = empty_send,
    ):
        super().__init__(scope, receive, send)
        self._json: Any = Void
        self.is_connected: bool = True
        self._parsed_query: Any = scope.get("_parsed_query", Void)

    @property
    def app(self) -> "Esmerald":
        """
        Returns:
            The [Esmerald][esmerald.applications.Esmerald] application instance
        """
        return cast("Esmerald", self.scope["app"])

    @property
    def user(self) -> User:
        """Allows access to user data.

        Raises:
            [ImproperlyConfigured][esmerald.exceptions.ImproperlyConfigured]: If 'user' is not set in scope via an 'AuthMiddleware', raises an exception

        Returns:
            A type correlating to the generic variable User.
        """
        if "user" not in self.scope:
            raise ImproperlyConfigured(
                "'user' is not defined in scope, install an AuthMiddleware to set it"
            )
        return cast("User", self.scope["user"])

    @property
    def query_params(self) -> Dict[str, Any]:  # type: ignore[override]
        """
        Returns:
            A normalized dict of query parameters. Multiple values for the same key are returned as a list.
        """
        if self._parsed_query is Void:
            self._parsed_query = self.scope["_parsed_query"] = parse_query_params(self)
        return cast("Dict[str, Any]", self._parsed_query)

    @property
    def method(self) -> "HTTPMethod":
        """
        Returns:
            The request [HTTPMethod][esmerald.types.HTTPMethod]
        """
        return cast("HTTPMethod", self.scope["method"])

    async def json(self):
        """
        Returns the json request from the body of the request.
        """
        if self._json is Void:
            if "_body" in self.scope:
                body = self.scope["_body"]
            else:
                body = self.scope["_body"] = await self.body() or "null".encode("utf-8")
            self._json = loads(body)
        return self._json
