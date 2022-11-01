import re
from typing import TYPE_CHECKING, List, Optional

from esmerald.routing.views import APIView
from esmerald.utils.helpers import clean_string, is_class_and_subclass
from esmerald.utils.url import clean_path
from starlette.routing import Route as StarletteRoute
from starlette.routing import WebSocketRoute as StarletteWebSocketRoute
from starlette.routing import compile_path
from starlette.types import Receive, Scope, Send

if TYPE_CHECKING:

    from esmerald.permissions.types import Permission
    from esmerald.routing.router import HTTPHandler, WebSocketHandler
    from esmerald.types import Dependencies, ExceptionHandlers, Middleware, ParentType


class Gateway(StarletteRoute):
    __slots__ = (
        "path",
        "handler",
        "name",
        "include_in_schema",
        "parent",
        "dependencies",
        "middleware",
        "exception_handlers",
        "permissions",
        "deprecated",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        handler: "HTTPHandler",
        name: Optional[str] = None,
        include_in_schema: bool = True,
        parent: Optional["ParentType"] = None,
        dependencies: Optional["Dependencies"] = None,
        middleware: Optional["Middleware"] = None,
        permissions: Optional["Permission"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        deprecated: Optional[bool] = None,
        is_from_router: bool = False,
    ) -> None:
        if not path:
            path = "/"
        if is_class_and_subclass(handler, APIView):
            handler = handler(parent=self)

        if not is_from_router:
            self.path = clean_path(path + handler.path)
        else:
            self.path = clean_path(path)
        self.methods = getattr(handler, "methods", None)

        if not name:
            if not isinstance(handler, APIView):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        super().__init__(
            path=self.path,
            endpoint=handler,
            include_in_schema=include_in_schema,
            name=name,
            methods=self.methods,
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Starlette Route endpoint does not understand the Esmerald handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self.handler = handler
        self.dependencies = dependencies or {}
        self.permissions = permissions or []
        self.middleware = middleware or []
        self.exception_handlers = exception_handlers or {}
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        (
            handler.path_regex,
            handler.path_format,
            handler.param_convertors,
        ) = compile_path(self.path)

        if not is_class_and_subclass(self.handler, APIView) and not isinstance(
            self.handler, APIView
        ):
            self.handler.get_response_handler()

            if not handler.operation_id:
                handler.operation_id = self.generate_operation_id()

    async def handle(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        await self.handler.handle(scope, receive, send)

    def generate_operation_id(self):
        """
        Generates an unique operation if for the handler
        """
        operation_id = self.name + self.handler.path_format
        operation_id = re.sub(r"\W", "_", operation_id)
        methods = [method for method in self.handler.methods]
        operation_id = f"{operation_id}_{methods[0].lower()}"
        return operation_id


class WebSocketGateway(StarletteWebSocketRoute):
    __slots__ = (
        "path",
        "handler",
        "name",
        "dependencies",
        "middleware",
        "exception_handlers",
        "permissions",
        "parent",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        handler: "WebSocketHandler",
        name: Optional[str] = None,
        parent: Optional["ParentType"] = None,
        dependencies: Optional["Dependencies"] = None,
        middleware: Optional[List["Middleware"]] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        permissions: Optional[List["Permission"]] = None,
    ) -> None:
        if not path:
            path = "/"
        if is_class_and_subclass(handler, APIView):
            handler = handler(parent=self)
        self.path = clean_path(path + handler.path)

        if not name:
            if not isinstance(handler, APIView):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        super().__init__(
            path=self.path,
            endpoint=handler,
            name=name,
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Starlette Route endpoint does not understand the Esmerald handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self.handler = handler
        self.dependencies = dependencies or {}
        self.permissions = permissions or []
        self.middleware = middleware or []
        self.exception_handlers = exception_handlers or {}
        self.parent = parent
        (
            handler.path_regex,
            handler.path_format,
            handler.param_convertors,
        ) = compile_path(self.path)

    async def handle(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        await self.handler.handle(scope, receive, send)
