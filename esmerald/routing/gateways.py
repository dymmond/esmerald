import re
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Sequence, Union, cast

from lilya._internal._path import clean_path
from lilya._utils import is_class_and_subclass
from lilya.middleware import DefineMiddleware
from lilya.routing import Path as LilyaPath, WebSocketPath as LilyaWebSocketPath, compile_path
from lilya.types import Receive, Scope, Send
from typing_extensions import Annotated, Doc

from esmerald.routing.apis.base import View
from esmerald.routing.base import BaseInterceptorMixin
from esmerald.typing import Void, VoidType
from esmerald.utils.helpers import clean_string

if TYPE_CHECKING:  # pragma: no cover
    from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme

    from esmerald.interceptors.types import Interceptor
    from esmerald.permissions.types import Permission
    from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler
    from esmerald.types import Dependencies, ExceptionHandlerMap, Middleware, ParentType


class BaseMiddleware:
    def handle_middleware(
        self, handler: Any, base_middleware: List["Middleware"]
    ) -> List["Middleware"]:
        """
        Handles both types of middlewares for Gateway and WebSocketGateway
        """
        _middleware: List["Middleware"] = []

        if not is_class_and_subclass(handler, View) and not isinstance(handler, View):
            base_middleware += handler.middleware or []

        for middleware in base_middleware or []:
            if isinstance(middleware, DefineMiddleware):
                _middleware.append(middleware)
            else:
                _middleware.append(DefineMiddleware(middleware))  # type: ignore
        return _middleware


class Gateway(LilyaPath, BaseInterceptorMixin, BaseMiddleware):
    """
    `Gateway` object class used by Esmerald routes.

    The Gateway act as a brigde between the router handlers and
    the main Esmerald routing system.

    Read more about [Gateway](https://esmerald.dev/routing/routes/#gateway) and
    how to use it.

    **Example**

    ```python
    from esmerald import Esmerald. get

    @get()
    async def home() -> str:
        return "Hello, World!"

    Gateway(path="/home", handler=home)
    ```
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "include_in_schema",
        "parent",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "deprecated",
        "tags",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                Gateway()
                ```

                **Example with parameters**

                ```python
                Gateway(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        *,
        handler: Annotated[
            Union["HTTPHandler", View],
            Doc(
                """
            An instance of [handler](https://esmerald.dev/routing/handlers/#http-handlers).
            """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://esmerald.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of a Gateway will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        is_from_router: Annotated[
            bool,
            Doc(
                """
                Used by the `.add_router()` function of the `Esmerald` class indicating if the
                Gateway is coming from a router.
                """
            ),
        ] = False,
        security: Annotated[
            Optional[Sequence["SecurityScheme"]],
            Doc(
                """
                Used by OpenAPI definition, the security must be compliant with the norms.
                Esmerald offers some out of the box solutions where this is implemented.

                The [Esmerald security](https://esmerald.dev/openapi/) is available to automatically used.

                The security can be applied also on a [level basis](https://esmerald.dev/application/levels/).

                For custom security objects, you **must** subclass
                `esmerald.openapi.security.base.HTTPBase` object.
                """
            ),
        ] = None,
        tags: Annotated[
            Optional[Sequence[str]],
            Doc(
                """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.
                """
            ),
        ] = None,
    ) -> None:
        if not path:
            path = "/"
        if is_class_and_subclass(handler, View):
            handler = handler(parent=self)  # type: ignore

        if not is_from_router:
            self.path = clean_path(path + handler.path)
        else:
            self.path = clean_path(path)

        self.methods = getattr(handler, "http_methods", None)

        if not name:
            if not isinstance(handler, View):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        # Handle middleware
        self.middleware = middleware or []
        self._middleware: List["Middleware"] = self.handle_middleware(
            handler=handler, base_middleware=self.middleware
        )
        super().__init__(
            path=self.path,
            handler=cast(Callable, handler),
            include_in_schema=include_in_schema,
            name=name,
            methods=self.methods,
            middleware=self._middleware,
            exception_handlers=exception_handlers,
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Lilya Route handler does not understand the Esmerald handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self._interceptors: Union[List["Interceptor"], "VoidType"] = Void
        self.name = name
        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}
        self.interceptors: Sequence["Interceptor"] = interceptors or []
        self.permissions: Sequence["Permission"] = permissions or []  # type: ignore
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.tags = tags or []
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )

        if not is_class_and_subclass(self.handler, View) and not isinstance(self.handler, View):
            self.handler.name = self.name

            if not handler.operation_id:
                handler.operation_id = self.generate_operation_id()

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        if self._middleware:
            self.is_middleware = True
        """
        await self.app(scope, receive, send)

    def generate_operation_id(self) -> str:
        """
        Generates an unique operation if for the handler
        """
        operation_id = self.name + self.handler.path_format
        operation_id = re.sub(r"\W", "_", operation_id)
        methods = list(self.handler.methods)

        assert self.handler.methods
        operation_id = f"{operation_id}_{methods[0].lower()}"
        return cast(str, operation_id)


class WebSocketGateway(LilyaWebSocketPath, BaseInterceptorMixin, BaseMiddleware):
    """
    `WebSocketGateway` object class used by Esmerald routes.

    The WebSocketGateway act as a brigde between the router handlers and
    the main Esmerald routing system.

    Read more about [WebSocketGateway](https://esmerald.dev/routing/routes/#websocketgateway) and
    how to use it.

    **Example**

    ```python
    from esmerald import Esmerald. websocket

    @websocket()
    async def world_socket(socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()

    WebSocketGateway(path="/ws", handler=home)
    ```
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "parent",
        "security",
        "tags",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `WebSocketGateway`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                WebSocketGateway()
                ```

                **Example with parameters**

                ```python
                WebSocketGateway(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        *,
        handler: Annotated[
            Union["WebSocketHandler", View],
            Doc(
                """
            An instance of [handler](https://esmerald.dev/routing/handlers/#websocket-handler).
            """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `path_for()`.
                """
            ),
        ] = None,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://esmerald.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional["Dependencies"],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List["Middleware"]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of a Gateway will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence["Interceptor"]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence["Permission"]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional["ExceptionHandlerMap"],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        is_from_router: Annotated[
            bool,
            Doc(
                """
                Used by the `.add_router()` function of the `Esmerald` class indicating if the
                Gateway is coming from a router.
                """
            ),
        ] = False,
    ) -> None:
        if not path:
            path = "/"
        if is_class_and_subclass(handler, View):
            handler = handler(parent=self)  # type: ignore

        if not is_from_router:
            self.path = clean_path(path + handler.path)
        else:
            self.path = clean_path(path)

        if not name:
            if not isinstance(handler, View):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        # Handle middleware
        self.middleware = middleware or []
        self._middleware: List["Middleware"] = self.handle_middleware(
            handler=handler, base_middleware=self.middleware
        )
        self.is_middleware: bool = False

        super().__init__(
            path=self.path,
            handler=cast("Callable", handler),
            name=name,
            middleware=self._middleware,
            exception_handlers=exception_handlers,
        )
        """
        A "bridge" to a handler and router mapping functionality.
        Since the default Lilya Route handler does not understand the Esmerald handlers,
        the Gateway bridges both functionalities and adds an extra "flair" to be compliant with both class based views and decorated function views.
        """
        self._interceptors: Union[List["Interceptor"], "VoidType"] = Void
        self.handler = cast("Callable", handler)
        self.dependencies = dependencies or {}
        self.interceptors = interceptors or []
        self.permissions = permissions or []  # type: ignore
        self.include_in_schema = False
        self.parent = parent
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )

    async def handle_dispatch(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Handles the interception of messages and calls from the API.
        if self._middleware:
            self.is_middleware = True
        """
        await self.app(scope, receive, send)


class WebhookGateway(LilyaPath, BaseInterceptorMixin):
    """
    `WebhookGateway` object class used by Esmerald routes.

    The WebhookGateway act as a brigde between the webhook handlers and
    the main Esmerald routing system.

    Read more about [WebhookGateway](https://esmerald.dev/routing/webhooks/) and
    how to use it.

    !!! Note
        This is used for OpenAPI documentation purposes only.
    """

    __slots__ = (
        "_interceptors",
        "path",
        "handler",
        "name",
        "include_in_schema",
        "parent",
        "dependencies",
        "middleware",
        "exception_handlers",
        "interceptors",
        "permissions",
        "security",
        "tags",
    )

    def __init__(
        self,
        *,
        handler: Annotated[
            Union["WebhookHandler", View],
            Doc(
                """
                An instance of [handler](https://esmerald.dev/routing/webhooks/#handlers).
                """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the WebhookGateway.
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
            ),
        ] = True,
        parent: Annotated[
            Optional["ParentType"],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://esmerald.dev/application/levels/).
                """
            ),
        ] = None,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
        security: Annotated[
            Optional[Sequence["SecurityScheme"]],
            Doc(
                """
                Used by OpenAPI definition, the security must be compliant with the norms.
                Esmerald offers some out of the box solutions where this is implemented.

                The [Esmerald security](https://esmerald.dev/openapi/) is available to automatically used.

                The security can be applied also on a [level basis](https://esmerald.dev/application/levels/).

                For custom security objects, you **must** subclass
                `esmerald.openapi.security.base.HTTPBase` object.
                """
            ),
        ] = None,
        tags: Annotated[
            Optional[Sequence[str]],
            Doc(
                """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.
                """
            ),
        ] = None,
    ) -> None:
        if is_class_and_subclass(handler, View):
            handler = handler(parent=self)  # type: ignore

        self.path = handler.path
        self.methods = getattr(handler, "http_methods", None)

        if not name:
            if not isinstance(handler, View):
                name = clean_string(handler.fn.__name__)
            else:
                name = clean_string(handler.__class__.__name__)

        self.handler = cast("Callable", handler)
        self.include_in_schema = include_in_schema

        self._interceptors: Union[List["Interceptor"], "VoidType"] = Void
        self.name = name
        self.dependencies: Any = {}
        self.interceptors: Sequence["Interceptor"] = []
        self.permissions: Sequence["Permission"] = []  # type: ignore
        self.middleware: Any = []
        self.exception_handlers: Any = {}
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.deprecated = deprecated
        self.parent = parent
        self.security = security
        self.tags = tags or []
        (handler.path_regex, handler.path_format, handler.param_convertors, _) = compile_path(
            self.path
        )

        if not is_class_and_subclass(self.handler, View) and not isinstance(self.handler, View):
            self.handler.name = self.name

            if not handler.operation_id:
                handler.operation_id = self.generate_operation_id()

    def generate_operation_id(self) -> str:
        """
        Generates an unique operation if for the handler
        """
        operation_id = self.name + self.handler.path_format
        operation_id = re.sub(r"\W", "_", operation_id)
        methods = list(self.handler.methods)

        assert self.handler.methods
        operation_id = f"{operation_id}_{methods[0].lower()}"
        return cast(str, operation_id)
