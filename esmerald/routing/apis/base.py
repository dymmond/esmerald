from copy import copy
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Union, cast

from starlette.routing import compile_path
from starlette.types import Receive, Scope, Send

from esmerald.utils.url import clean_path

if TYPE_CHECKING:  # pragma: no cover
    from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme

    from esmerald.interceptors.types import Interceptor
    from esmerald.permissions.types import Permission
    from esmerald.routing.gateways import Gateway, WebSocketGateway
    from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler
    from esmerald.transformers.model import TransformerModel
    from esmerald.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


class View:
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
        "route_map",
        "operation_id",
        "methods",
        "interceptors",
        "security",
    )

    path: str
    dependencies: Optional["Dependencies"]
    exception_handlers: Optional["ExceptionHandlerMap"]
    permissions: Optional[List["Permission"]]
    middleware: Optional[List["Middleware"]]
    parent: Union["Gateway", "WebSocketGateway"]
    response_class: Optional["ResponseType"]
    response_cookies: Optional["ResponseCookies"]
    response_headers: Optional["ResponseHeaders"]
    tags: Optional[List[str]]
    deprecated: Optional[bool]
    include_in_schema: Optional[bool]
    interceptors: Optional[Sequence["Interceptor"]]
    security: Optional[List["SecurityScheme"]]

    def __init__(self, parent: Union["Gateway", "WebSocketGateway"]) -> None:
        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.path = clean_path(self.path or "/")
        self.path_regex, self.path_format, self.param_convertors = compile_path(self.path)
        self.parent = parent
        self.route_map: Dict[str, Tuple["HTTPHandler", "TransformerModel"]] = {}
        self.operation_id: Optional[str] = None
        self.methods: List[str] = []

    def get_filtered_handler(self) -> List[str]:
        """
        Filters out the names of the functions that are not part of the handler itself.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        filtered_handlers = [
            attr for attr in dir(self) if not attr.startswith("__") and not attr.endswith("__")
        ]
        route_handlers = []

        for handler_name in filtered_handlers:
            for base in self.__class__.__bases__:
                if handler_name not in dir(base) and isinstance(
                    getattr(self, handler_name), (HTTPHandler, WebSocketHandler, WebhookHandler)
                ):
                    route_handlers.append(handler_name)
        return route_handlers

    def get_route_handlers(
        self,
    ) -> List[Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]]:
        """A getter for the apiview's route handlers that sets their parent.

        Returns:
            A list containing a copy of the route handlers defined inside the View.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        route_handlers: List[Union[HTTPHandler, WebSocketHandler, WebhookHandler]] = []
        filtered_handlers = self.get_filtered_handler()

        for handler in filtered_handlers:
            source_route_handler = cast(
                Union["HTTPHandler", "WebSocketHandler"], getattr(self, handler)
            )
            route_handler = copy(source_route_handler)
            route_handler.parent = self

            if self.include_in_schema is not None and not isinstance(
                route_handler, WebSocketHandler
            ):  # pragma: no cover
                route_handler.include_in_schema = self.include_in_schema

            if self.middleware:
                self.get_route_middleware(route_handler)

            if self.exception_handlers:
                route_handler.exception_handlers = self.get_exception_handlers(route_handler)
            if self.tags or []:  # pragma: no cover
                for tag in reversed(self.tags):
                    route_handler.tags.insert(0, tag)
            route_handlers.append(route_handler)

        return route_handlers

    def get_route_middleware(
        self, handler: Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]
    ) -> None:
        """
        Gets the list of extended middlewares for the handler starting from the last
        to the first by reversing the list
        """
        for middleware in reversed(self.middleware):
            handler.middleware.insert(0, middleware)

    def get_exception_handlers(
        self, handler: Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]
    ) -> "ExceptionHandlerMap":
        """
        Gets the dict of extended exception handlers for the handler starting from the last
        to the first by reversing the list
        """
        exception_handlers = {**self.exception_handlers, **handler.exception_handlers}
        return cast("ExceptionHandlerMap", exception_handlers)

    async def handle(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:  # pragma: no cover
        raise NotImplementedError(f"{self.__class__.__name__} object does not implement handle()")

    def create_signature_model(self, is_websocket: bool = False) -> None:  # pragma: no cover
        raise NotImplementedError(
            f"{self.__class__.__name__} object does not implement create_signature_model()"
        )
