from copy import copy
from typing import TYPE_CHECKING, List, Optional, Union, cast

from starlette.routing import compile_path

from esmerald.utils.url import clean_path

if TYPE_CHECKING:
    from esmerald.permissions.types import Permission
    from esmerald.routing.router import HTTPHandler, Router, WebSocketHandler
    from esmerald.types import (
        Dependencies,
        ExceptionHandlers,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


class APIView:
    """The Esmerald APIView class.

    Subclassing this class will create a view using Class Based Views.
    """

    __slots__ = (
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "parent",
        "path",
        "response_class",
        "response_cookies",
        "response_headers",
        "tags",
        "path_regex",
        "path_format",
        "param_convertors",
        "deprecated",
        "include_in_schema",
    )

    path: str
    dependencies: Optional["Dependencies"]
    exception_handlers: Optional["ExceptionHandlers"]
    permissions: Optional[List["Permission"]]
    middleware: Optional[List["Middleware"]]
    parent: "Router"
    response_class: Optional["ResponseType"]
    response_cookies: Optional["ResponseCookies"]
    response_headers: Optional["ResponseHeaders"]
    tags: Optional[List[str]]
    deprecated: Optional[bool]
    include_in_schema: Optional[bool]

    def __init__(self, parent: "Router") -> None:
        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.path = clean_path(self.path or "/")
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path)
        self.parent = parent
        self.interceptors = []

    def get_filtered_handler(self) -> List[str]:
        """
        Filters out the names of the functions that are not part of the handler itself.
        """
        from esmerald.routing.router import HTTPHandler, WebSocketHandler

        filtered_handlers = [
            attr for attr in dir(self) if not attr.startswith("__") and not attr.endswith("__")
        ]
        route_handlers = []

        for handler_name in filtered_handlers:

            if handler_name not in dir(APIView) and isinstance(
                getattr(self, handler_name), (HTTPHandler, WebSocketHandler)
            ):
                route_handlers.append(handler_name)
        return route_handlers

    def get_route_handlers(self) -> List[Union["HTTPHandler", "WebSocketHandler"]]:
        """A getter for the apiview's route handlers that sets their parent.

        Returns:
            A list containing a copy of the route handlers defined inside the APIView.
        """
        from esmerald.routing.router import HTTPHandler, WebSocketHandler

        route_handlers: List[Union[HTTPHandler, WebSocketHandler]] = []
        filtered_handlers = self.get_filtered_handler()

        for handler in filtered_handlers:
            source_route_handler = cast(
                Union["HTTPHandler", "WebSocketHandler"], getattr(self, handler)
            )
            route_handler = copy(source_route_handler)
            route_handler.parent = self

            if self.include_in_schema is not None and not isinstance(
                route_handler, WebSocketHandler
            ):
                route_handler.include_in_schema = self.include_in_schema

            if self.middleware:
                self.get_route_middleware(route_handler)

            if self.exception_handlers:
                route_handler.exception_handlers = self.get_exception_handlers(route_handler)
            if self.tags or []:
                for tag in reversed(self.tags):
                    route_handler.tags.insert(0, tag)
            route_handlers.append(route_handler)

        return route_handlers

    def get_route_middleware(
        self, handler: Union["HTTPHandler", "WebSocketHandler"]
    ) -> List["Middleware"]:
        """
        Gets the list of extended middlewares for the handler starting from the last
        to the first by reversing the list
        """
        for middleware in reversed(self.middleware):
            handler.middleware.insert(0, middleware)

    def get_exception_handlers(
        self, handler: Union["HTTPHandler", "WebSocketHandler"]
    ) -> "ExceptionHandlers":
        """
        Gets the dict of extended exception handlers for the handler starting from the last
        to the first by reversing the list
        """
        exception_handlers = {**self.exception_handlers, **handler.exception_handlers}
        return exception_handlers
