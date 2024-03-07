from __future__ import annotations

import inspect
from copy import copy
from enum import IntEnum
from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from starlette import status
from starlette.datastructures import URLPath
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse, Response as StarletteResponse
from starlette.routing import (
    BaseRoute as StarletteBaseRoute,
    Host,
    Mount,
    NoMatchFound,
    Route as StarletteRoute,
    Router as StarletteRouter,
    WebSocketRoute as StarletteWebSocketRoute,
    compile_path,
)
from starlette.types import ASGIApp, Lifespan, Receive, Scope, Send
from typing_extensions import Annotated, Doc

from esmerald.conf import settings
from esmerald.core.urls import include
from esmerald.datastructures import File, Redirect
from esmerald.enums import HttpMethod, MediaType
from esmerald.exceptions import (
    ImproperlyConfigured,
    MethodNotAllowed,
    NotFound,
    OpenAPIException,
    ValidationErrorException,
)
from esmerald.interceptors.types import Interceptor
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.openapi.utils import is_status_code_allowed
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing._internal import FieldInfoMixin
from esmerald.routing.apis.base import View
from esmerald.routing.base import BaseInterceptorMixin
from esmerald.routing.events import handle_lifespan_events
from esmerald.routing.gateways import Gateway, WebhookGateway, WebSocketGateway
from esmerald.transformers.datastructures import EsmeraldSignature as SignatureModel
from esmerald.transformers.model import TransformerModel
from esmerald.transformers.utils import get_signature
from esmerald.typing import Void, VoidType
from esmerald.utils.constants import DATA, PAYLOAD, REDIRECT_STATUS_CODES, REQUEST, SOCKET
from esmerald.utils.helpers import is_async_callable, is_class_and_subclass
from esmerald.utils.module_loading import import_string
from esmerald.utils.url import clean_path
from esmerald.websockets import WebSocket, WebSocketClose

if TYPE_CHECKING:  # pragma: no cover
    from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme

    from esmerald.applications import Esmerald
    from esmerald.permissions.types import Permission
    from esmerald.types import (
        APIGateHandler,
        AsyncAnyCallable,
        BackgroundTaskType,
        Dependencies,
        ExceptionHandlerMap,
        LifeSpanHandler,
        Middleware,
        ParentType,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
        RouteParent,
    )
    from esmerald.typing import AnyCallable


class BaseRouter(StarletteRouter):
    __slots__ = (
        "redirect_slashes",
        "default",
        "name",
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "response_class",
        "response_cookies",
        "response_headers",
        "parent",
        "tags",
        "deprecated",
        "security",
        "on_startup",
        "on_shutdown",
        "root_path",
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
                Include()
                ```

                **Example with parameters**

                ```python
                Include(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        app: Annotated[
            Optional[Esmerald],
            Doc(
                """
                A `Router` instance always expects an `Esmerald` instance
                as an app or any subclass of Esmerald, like a `ChildEsmerald`.

                **Example**

                ```python
                from esmerald import ChildEsmerald, Router

                Router('/child', app=ChildEsmerald(...))
                ```
                """
            ),
        ] = None,
        parent: Annotated[
            Optional[ParentType],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://esmerald.dev/application/levels/).
                """
            ),
        ] = None,
        on_startup: Annotated[
            Optional[List[LifeSpanHandler]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                starts.

                Read more about the [events](https://esmerald.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from esmerald import Router, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Router(
                    routes=[Gateway(handler=create_user)],
                    on_startup=[database.connect],
                )
                ```
                """
            ),
        ] = None,
        on_shutdown: Annotated[
            Optional[List[LifeSpanHandler]],
            Doc(
                """
                A `list` of events that are trigger upon the application
                shuts down.

                Read more about the [events](https://esmerald.dev/lifespan-events/).

                **Example**

                ```python
                from pydantic import BaseModel
                from saffier import Database, Registry

                from esmerald import Router, Gateway, post

                database = Database("postgresql+asyncpg://user:password@host:port/database")
                registry = Registry(database=database)


                class User(BaseModel):
                    name: str
                    email: str
                    password: str
                    retype_password: str


                @post("/create", tags=["user"], description="Creates a new user in the database")
                async def create_user(data: User) -> None:
                    # Logic to create the user
                    ...


                app = Router(
                    routes=[Gateway(handler=create_user)],
                    on_shutdown=[database.disconnect],
                )
                ```
                """
            ),
        ] = None,
        redirect_slashes: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag indicating if the redirect slashes are enabled for the
                routes or not.
                """
            ),
        ] = None,
        default: Annotated[
            Optional[ASGIApp],
            Doc(
                """
                A `default` ASGI callable.
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[Sequence[Union[APIGateHandler, Include]]],
            Doc(
                """
                A `list` of esmerald routes. Those routes may vary and those can
                be `Gateway`, `WebSocketGateWay` or even an `Include`.

                This is also an entry-point for the routes of the `Router`
                but it **does not rely on only one [level](https://esmerald.dev/application/levels/)**.

                Read more about how to use and leverage
                the [Esmerald routing system](https://esmerald.dev/routing/routes/).

                **Example**

                ```python
                from esmerald import Esmerald, Gateway, Request, get, Include


                @get()
                async def homepage(request: Request) -> str:
                    return "Hello, home!"


                @get()
                async def another(request: Request) -> str:
                    return "Hello, another!"

                app = Esmerald(
                    routes=[
                        Gateway(handler=homepage)
                        Include("/nested", routes=[
                            Gateway(handler=another)
                        ])
                    ]
                )
                ```

                !!! Note
                    The Include is very powerful and this example
                    is not enough to understand what more things you can do.
                    Read in [more detail](https://esmerald.dev/routing/routes/#include) about this.
                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Starlette Middleware](https://www.starlette.io/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        response_class: Annotated[
            Optional[ResponseType],
            Doc(
                """
                Default response class to be used within the
                Esmerald application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import Router, JSONResponse

                Router(response_class=JSONResponse)
                ```
                """
            ),
        ] = None,
        response_cookies: Annotated[
            Optional[ResponseCookies],
            Doc(
                """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import Router
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                Router(response_cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        response_headers: Annotated[
            Optional[ResponseHeaders],
            Doc(
                """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import Router
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                Router(response_headers=response_headers)
                ```
                """
            ),
        ] = None,
        lifespan: Annotated[
            Optional[Lifespan[Any]],
            Doc(
                """
                A `lifespan` context manager handler. This is an alternative
                to `on_startup` and `on_shutdown` and you **cannot used all combined**.

                Read more about the [lifespan](https://esmerald.dev/lifespan-events/).
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
        deprecated: Optional[bool] = None,
        security: Annotated[
            Optional[Sequence[SecurityScheme]],
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
    ):
        self._app = app
        if not path:
            path = "/"
        else:
            assert path.startswith("/"), "A path prefix must start with '/'"
            assert not path.endswith(
                "/"
            ), "A path must not end with '/', as the routes will start with '/'"

        for route in routes or []:
            if not isinstance(
                route,
                (
                    Include,
                    Gateway,
                    WebSocketGateway,
                    StarletteBaseRoute,
                    Mount,
                    Host,
                    Router,
                ),
            ) or isinstance(route, WebhookGateway):
                raise ImproperlyConfigured(
                    f"The route {route} must be of type Gateway, WebSocketGateway or Include"
                )

        assert lifespan is None or (
            on_startup is None and on_shutdown is None
        ), "Use either 'lifespan' or 'on_startup'/'on_shutdown', not both."

        self.esmerald_lifespan = handle_lifespan_events(
            on_startup=on_startup, on_shutdown=on_shutdown, lifespan=lifespan
        )

        super().__init__(
            redirect_slashes=redirect_slashes,
            routes=routes,
            default=default,
            lifespan=self.esmerald_lifespan,
        )
        self.path = path
        self.on_startup = [] if on_startup is None else list(on_startup)
        self.on_shutdown = [] if on_shutdown is None else list(on_shutdown)
        self.parent: Optional[ParentType] = parent or app
        self.dependencies = dependencies or {}
        self.exception_handlers = exception_handlers or {}
        self.interceptors: Sequence[Interceptor] = interceptors or []
        self.permissions: Sequence[Permission] = permissions or []
        self.routes: Any = routes or []
        self.middleware = middleware or []
        self.tags = tags or []
        self.name = name
        self.response_class = response_class
        self.response_cookies = response_cookies or []
        self.response_headers = response_headers or {}
        self.deprecated = deprecated
        self.security = security or []

        self.routing = copy(self.routes)
        for route in self.routing or []:
            self.validate_root_route_parent(route)

        for route in self.routes or []:
            self.create_signature_models(route)

        self.activate()

    def reorder_routes(self) -> List[Sequence[Union[APIGateHandler, Include]]]:
        routes = sorted(
            self.routes,
            key=lambda router: router.path != "" and router.path != "/",
            reverse=True,
        )
        return routes

    def activate(self) -> None:
        self.routes = self.reorder_routes()

    async def not_found(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:  # pragma: no cover
        """Esmerald version of a not found handler when a resource is
        called and cannot be dealt with properly.

        Esmerald overrides the original Starlette not_found to return always
        JSONReponse.

        For plain ASGI apps, just returns the response.
        """
        if scope["type"] == "websocket":
            websocket_close = WebSocketClose()
            await websocket_close(scope, receive, send)
            return

        if "app" in scope:
            raise NotFound(status_code=status.HTTP_404_NOT_FOUND)
        else:
            response = JSONResponse({"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND)
        await response(scope, receive, send)

    def url_path_for(self, name: str, **path_params: Any) -> URLPath:
        for route in self.routes or []:
            try:
                return cast("URLPath", route.url_path_for(name, **path_params))
            except NoMatchFound:
                ...

            if isinstance(route, (Gateway, WebSocketGateway)):
                handler = cast("Union[HTTPHandler, WebSocketHandler]", route.handler)
                try:
                    return handler.url_path_for(name, **path_params)
                except NoMatchFound:
                    ...

        raise NoMatchFound(name, path_params)

    def add_event_handler(self, event_type: str, func: Callable) -> None:  # pragma: no cover
        assert event_type in ("startup", "shutdown")

        if event_type == "startup":
            self.on_startup.append(func)

        else:
            self.on_shutdown.append(func)

    def on_event(self, event_type: str) -> Callable:  # pragma: no cover
        def decorator(func: Callable) -> Callable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    def create_signature_models(self, route: RouteParent) -> None:
        """
        Creates the signature models for the given routes.

        Args:
            route: The route for the signature model to be created.
        """
        if isinstance(route, (Include, Host)):
            for _route in route.routes:
                self.create_signature_models(_route)

        if isinstance(route, (Gateway, WebhookGateway)):
            if not route.handler.parent:  # pragma: no cover
                route.handler.parent = route  # type: ignore

            if not is_class_and_subclass(route.handler, View) and not isinstance(
                route.handler, View
            ):
                route.handler.create_signature_model()

        if isinstance(route, WebSocketGateway):
            route.handler.create_signature_model(is_websocket=True)

    def validate_root_route_parent(
        self,
        value: Union[Router, Include, Gateway, WebSocketGateway, WebhookGateway],
        override: bool = False,
    ) -> None:
        """
        Handles everything parent from the root. When in the root, the parent must be setup.
        Appends the route path if exists.
        """
        # Getting the value of the router for the path
        value.path = clean_path(self.path + getattr(value, "path", "/"))

        if isinstance(value, (Include, Gateway, WebSocketGateway, WebSocketGateway)):
            if not value.parent and not override:
                value.parent = cast("Union[Router, Include, Gateway, WebSocketGateway]", self)

        if isinstance(value, (Gateway, WebSocketGateway, WebhookGateway)):
            if not is_class_and_subclass(value.handler, View) and not isinstance(
                value.handler, View
            ):
                if not value.handler.parent:
                    value.handler.parent = value  # type: ignore
            else:
                if not value.handler.parent:  # pragma: no cover
                    value(parent=self)  # type: ignore

                handler: View = cast("View", value.handler)
                route_handlers = handler.get_route_handlers()
                for route_handler in route_handlers:
                    gateway = (
                        Gateway
                        if not isinstance(route_handler, WebSocketHandler)
                        else WebSocketGateway
                    )

                    gate = gateway(
                        path=value.path,
                        handler=route_handler,
                        name=route_handler.fn.__name__,
                        middleware=value.middleware,
                        interceptors=value.interceptors,
                        permissions=value.permissions,
                        exception_handlers=value.exception_handlers,
                    )

                    if isinstance(gate, (Gateway, WebhookGateway)):
                        include_in_schema = (
                            value.include_in_schema
                            if value.include_in_schema is not None
                            else route_handler.include_in_schema
                        )
                        gate.include_in_schema = include_in_schema

                    self.routes.append(gate)
                self.routes.pop(self.routes.index(value))


class Router(BaseRouter):
    """
    The `Router` object used by `Esmerald` upon instantiation.

    The router is what is created by default when the `routes` parameter is
    defined.

    This object is complex and very powerful. Read more in detail about [the Router](https://esmerald.dev/routing/router/) and how to use it.

    """

    def add_apiview(
        self,
        value: Annotated[
            Union[Gateway, WebSocketGateway],
            Doc(
                """
                The `APIView` or similar to be added.
                """
            ),
        ],
    ) -> None:
        """
        Adds an [APIView](https://esmerald.dev/routing/apiview/) or related
        to the application routing.

        **Example**

        ```python
        from esmerald import Router, APIView, Gateway, get

        class View(APIView):
            path = "/"

            @get(status_code=status_code)
            async def hello(self) -> str:
                return "Hello, World!"

        gateway = Gateway(handler=View)

        app = Router()
        app.add_apiview(value=gateway)
        ```
        """
        routes = []
        if not value.handler.parent:  # pragma: no cover
            value.handler(parent=self)  # type: ignore

        route_handlers: List[Union[HTTPHandler, WebSocketHandler]] = value.handler.get_route_handlers()  # type: ignore
        for route_handler in route_handlers:
            gateway = (
                Gateway if not isinstance(route_handler, WebSocketHandler) else WebSocketGateway
            )
            gate = gateway(
                path=value.path,
                handler=route_handler,
                name=route_handler.path,
                middleware=value.middleware,
                interceptors=value.interceptors,
                include_in_schema=value.include_in_schema,
                permissions=value.permissions,
                exception_handlers=value.exception_handlers,
            )
            self.routes.append(gate)
            routes.append(gate)

        for route in routes or []:
            self.create_signature_models(route)
        self.activate()

    def add_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            HTTPHandler,
            Doc(
                """
                An instance of [handler](https://esmerald.dev/routing/handlers/#http-handlers).
                """
            ),
        ],
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Starlette Middleware](https://www.starlette.io/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
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
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Gateway and to display it
                in the OpenAPI documentation..
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a [Route](https://esmerald.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from esmerald import get

        @get(status_code=status_code)
        async def hello(self) -> str:
            return "Hello, World!"

        app = Esmerald()
        app.add_route(path="/hello", handler=hello)
        ```
        """
        if not isinstance(handler, HTTPHandler):
            raise ImproperlyConfigured(
                f"handler must be a instance of HTTPHandler and not {handler.__class__.__name__}. "
                "Example: get(), put(), post(), delete(), patch(), route()."
            )
        gateway = Gateway(
            path=self.path + path,
            handler=handler,
            name=name,
            include_in_schema=include_in_schema,
            dependencies=dependencies,
            exception_handlers=cast("ExceptionHandlerMap", exception_handlers),
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
            deprecated=deprecated,
        )
        self.validate_root_route_parent(gateway)
        self.create_signature_models(gateway)
        self.routes.append(gateway)

    def add_websocket_route(
        self,
        path: Annotated[
            str,
            Doc(
                """
                Relative path of the `Gateway`.
                The path can contain parameters in a dictionary like format.
                """
            ),
        ],
        handler: Annotated[
            WebSocketHandler,
            Doc(
                """
                An instance of [websocket handler](https://esmerald.dev/routing/handlers/#websocket-handler).
                """
            ),
        ],
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Starlette Middleware](https://www.starlette.io/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
    ) -> None:
        """
        Adds a websocket [Route](https://esmerald.dev/routing/routes/)
        to the application routing.

        This is a dynamic way of adding routes on the fly.

        **Example**

        ```python
        from esmerald import websocket

        @websocket()
        async def websocket_route(socket: WebSocket) -> None:
            await socket.accept()
            data = await socket.receive_json()

            assert data
            await socket.send_json({"data": "esmerald"})
            await socket.close()

        app = Esmerald()
        app.add_websocket_route(path="/ws", handler=websocket_route)
        ```
        """
        if not isinstance(handler, WebSocketHandler):
            raise ImproperlyConfigured(
                f"handler must be a instance of WebSocketHandler and not {handler.__class__.__name__}. "
                "Example: websocket()."
            )
        websocket_gateway = WebSocketGateway(
            path=path,
            handler=handler,
            name=name,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            interceptors=interceptors,
            permissions=permissions,
            middleware=middleware,
        )
        self.validate_root_route_parent(websocket_gateway)
        self.create_signature_models(websocket_gateway)
        self.routes.append(websocket_gateway)


class HTTPHandler(BaseInterceptorMixin, FieldInfoMixin, StarletteRoute):
    __slots__ = (
        "path",
        "_interceptors",
        "_permissions",
        "_dependencies",
        "_response_handler",
        "_middleware",
        "methods",
        "status_code",
        "content_encoding",
        "media_type",
        "content_media_type",
        "summary",
        "description",
        "include_in_schema",
        "dependencies",
        "exception_handlers",
        "permissions",
        "middleware",
        "response_class",
        "response_cookies",
        "response_headers",
        "parent",
        "tags",
        "deprecated",
        "security",
        "operation_id",
        "interceptors",
        "__type__",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        endpoint: Callable[..., Any] = None,
        *,
        methods: Optional[Sequence[str]] = None,
        status_code: Optional[int] = None,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional[BackgroundTaskType] = None,
        dependencies: Optional[Dependencies] = None,
        exception_handlers: Optional[ExceptionHandlerMap] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[Sequence[str]] = None,
        deprecated: Optional[bool] = None,
        response_description: Optional[str] = "Successful Response",
        responses: Optional[Dict[int, OpenAPIResponse]] = None,
        security: Optional[List[SecurityScheme]] = None,
        operation_id: Optional[str] = None,
    ) -> None:
        """
        Handles the "handler" or "apiview" of the platform. A handler can be any get, put, patch, post, delete or route.
        """
        if not path:
            path = "/"
        super().__init__(path=path, endpoint=endpoint, include_in_schema=include_in_schema)

        self._permissions: Union[List[Permission], VoidType] = Void
        self._dependencies: Dependencies = {}

        self._response_handler: Union[Callable[[Any], Awaitable[StarletteResponse]], VoidType] = (
            Void
        )

        self.parent: ParentType = None
        self.path = path
        self.endpoint = endpoint
        self.summary = summary
        self.tags = tags or []
        self.include_in_schema = include_in_schema
        self.deprecated = deprecated

        if not self.deprecated:
            self.deprecated = False

        self.security = security or []
        self.operation_id = operation_id

        if not methods:
            methods = [HttpMethod.GET.value]

        for method in methods or []:
            if not isinstance(method, str):
                raise ImproperlyConfigured(f"`{method}` in `methods` must be a string.")

        self.methods: Set[str] = {HttpMethod[method].value for method in methods}

        if isinstance(status_code, IntEnum):  # pragma: no cover
            status_code = int(status_code)
        self.status_code = status_code

        self.exception_handlers = exception_handlers or {}
        self.dependencies: Dependencies = dependencies or {}
        self.description = description or inspect.cleandoc(self.endpoint.__doc__ or "")
        self.permissions = list(permissions) if permissions else []
        self.interceptors: Sequence[Interceptor] = []
        self.middleware = list(middleware) if middleware else []
        self.description = self.description.split("\f")[0]
        self.media_type = media_type
        self.response_class = response_class
        self.response_cookies = response_cookies
        self.response_headers = response_headers
        self.background = background
        self.signature_model: Optional[Type[SignatureModel]] = None
        self.transformer: Optional[TransformerModel] = None
        self.response_description = response_description
        self.responses = responses or {}
        self.content_encoding = content_encoding
        self.content_media_type = content_media_type

        self.fn: Optional[AnyCallable] = None
        self.route_map: Dict[str, Tuple[HTTPHandler, TransformerModel]] = {}
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)
        self._middleware: List[Middleware] = []
        self._interceptors: Union[List[Interceptor], VoidType] = Void
        self.__type__: Union[str, None] = None

        if self.responses:
            self.validate_responses(responses=self.responses)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        await self.handle(scope=scope, receive=receive, send=send)

    def validate_responses(self, responses: Dict[int, OpenAPIResponse]) -> None:
        """
        Checks if the responses are valid or raises an exception otherwise.
        """
        for status_code, response in responses.items():
            if not isinstance(response, OpenAPIResponse):
                raise OpenAPIException(
                    detail="An additional response must be an instance of OpenAPIResponse."
                )

            if not is_status_code_allowed(status_code):
                raise OpenAPIException(detail="The status is not a valid OpenAPI status response.")

    @property
    def http_methods(self) -> List[str]:
        """
        Converts the methods set into a list of methods.
        """
        return list(self.methods)

    async def allowed_methods(
        self, scope: "Scope", receive: "Receive", send: "Send", methods: List[str]
    ) -> None:
        """
        Validates if the scope method is available within the handler and raises
        a MethodNotAllowed if otherwise.
        """
        for method in methods:
            if method not in self.http_methods:
                raise MethodNotAllowed(detail=f"Method {method.upper()} not allowed.")

    @property
    def allow_header(self) -> Mapping[str, str]:
        """
        Default allow header to be injected in the Response and Starlette Response type
        handlers.
        """
        return {"allow": str(self.methods)}

    def get_response_class(self) -> Type[Response]:
        """
        Returns the closest custom Response class in the parent graph or the
        default Response class.
        """
        response_class = Response
        for layer in self.parent_levels:
            if layer.response_class is not None:
                response_class = layer.response_class
        return response_class

    def get_response_headers(self) -> ResponseHeaders:
        """
        Returns all header parameters in the scope of the handler function.
        """
        resolved_response_headers: ResponseHeaders = {}
        for layer in self.parent_levels:
            resolved_response_headers.update(layer.response_headers or {})
        return resolved_response_headers

    def get_response_cookies(self) -> ResponseCookies:
        """Returns a list of Cookie instances. Filters the list to ensure each
        cookie key is unique.
        """

        cookies: ResponseCookies = []
        for layer in self.parent_levels:
            cookies.extend(layer.response_cookies or [])
        filtered_cookies: ResponseCookies = []
        for cookie in reversed(cookies):
            if not any(cookie.key == c.key for c in filtered_cookies):
                filtered_cookies.append(cookie)
        return filtered_cookies

    async def handle(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        ASGIapp that authorizes the connection and then awaits the handler function.
        """
        if self.get_interceptors():
            await self.intercept(scope, receive, send)

        methods = [scope["method"]]
        await self.allowed_methods(scope, receive, send, methods)

        request = Request(scope=scope, receive=receive, send=send)
        route_handler, parameter_model = self.route_map[scope["method"]]

        if self.get_permissions():
            connection = HTTPConnection(scope=scope, receive=receive)
            await self.allow_connection(connection)

        response = await self.get_response_for_request(
            scope=scope,
            request=request,
            route=route_handler,
            parameter_model=parameter_model,
        )
        await response(scope, receive, send)

    def check_handler_function(self) -> None:
        """Validates the route handler function once it's set by inspecting its
        return annotations.

        `enable_sync_handlers` from the application settings enables/disables the possibility
        of having `sync` handlers.

        Example:
            enable_sync_handlers = True

            @get(path'/')
            def index(request: Request) -> Response:
                return Response("Welcome Home")

            enable_sync_handlers = False

            @get(path'/')
            async def index(request: Request) -> Response:
                return Response("Welcome Home")

        Raises:
            ImproperlyConfigured if enable_sync_handlers is False and the function is sync.
        """
        if not self.fn:
            raise ImproperlyConfigured(
                "Cannot call check_handler_function without first setting self.fn"
            )

        if not settings.enable_sync_handlers:  # pragma: no cover
            fn = cast("AnyCallable", self.fn)
            if not is_async_callable(fn):
                raise ImproperlyConfigured(
                    "Functions decorated with 'route, websocket, get, patch, put, post and delete' must be async functions"
                )

    def validate_annotations(self) -> None:  # pragma: no cover
        """
        Validate annotations of the handlers.
        """
        return_annotation = self.signature.return_annotation

        if return_annotation is Signature.empty:
            raise ImproperlyConfigured(
                "A return value of a route handler function should be type annotated. "
                "If your function doesn't return a value or returns None, annotate it as returning 'NoReturn' or 'None' respectively."
            )
        if (
            self.status_code < status.HTTP_200_OK
            or self.status_code in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
        ) and return_annotation not in [NoReturn, None]:
            raise ImproperlyConfigured(
                "A status code 204, 304 or in the range below 200 does not support a response body."
                " If the function should return a value, change the route handler status code to an appropriate value.",
            )
        if (
            is_class_and_subclass(return_annotation, Redirect)
            and self.status_code not in REDIRECT_STATUS_CODES
        ):
            raise ValidationErrorException(
                f"Redirect responses should have one of "
                f"the following status codes: {', '.join([str(s) for s in REDIRECT_STATUS_CODES])}"
            )
        if is_class_and_subclass(return_annotation, File) and self.media_type in [
            MediaType.JSON,
            MediaType.HTML,
        ]:
            self.media_type = MediaType.TEXT

    def validate_reserved_kwargs(self) -> None:  # pragma: no cover
        """
        Validates if special words are in the signature.
        """
        if DATA in self.signature.parameters and "GET" in self.methods:
            raise ImproperlyConfigured("'data' argument is unsupported for 'GET' request handlers")

        if PAYLOAD in self.signature.parameters and "GET" in self.methods:
            raise ImproperlyConfigured(
                "'payload' argument is unsupported for 'GET' request handlers"
            )

        if SOCKET in self.signature.parameters:
            raise ImproperlyConfigured("The 'socket' argument is not supported with http handlers")

    def validate_handler(self) -> None:
        self.check_handler_function()
        self.validate_annotations()
        self.validate_reserved_kwargs()

    async def to_response(self, app: "Esmerald", data: Any) -> StarletteResponse:
        response_handler = self.get_response_handler()
        return await response_handler(app=app, data=data)  # type: ignore[call-arg]


class WebhookHandler(HTTPHandler, FieldInfoMixin, StarletteRoute):
    """
    Base for a webhook handler.
    """

    _slots__ = (
        "path",
        "_permissions",
        "_dependencies",
        "_response_handler",
        "_middleware",
        "methods",
        "status_code",
        "content_encoding",
        "media_type",
        "content_media_type",
        "summary",
        "description",
        "include_in_schema",
        "dependencies",
        "exception_handlers",
        "permissions",
        "middleware",
        "response_class",
        "response_cookies",
        "response_headers",
        "parent",
        "tags",
        "deprecated",
        "security",
        "operation_id",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        endpoint: Callable[..., Any] = None,
        *,
        methods: Optional[Sequence[str]] = None,
        status_code: Optional[int] = None,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional[BackgroundTaskType] = None,
        dependencies: Optional[Dependencies] = None,
        exception_handlers: Optional[ExceptionHandlerMap] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[Sequence[str]] = None,
        deprecated: Optional[bool] = None,
        response_description: Optional[str] = "Successful Response",
        responses: Optional[Dict[int, OpenAPIResponse]] = None,
        security: Optional[List[SecurityScheme]] = None,
        operation_id: Optional[str] = None,
    ) -> None:
        _path: str = None
        if not path:
            _path = "/"  # pragma: no cover
        super().__init__(
            path=_path,
            endpoint=endpoint,
            methods=methods,
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        self.path = path


class WebSocketHandler(BaseInterceptorMixin, StarletteWebSocketRoute):
    """
    Websocket handler object representation.
    """

    __slots__ = (
        "path",
        "dependencies",
        "exception_handlers",
        "permissions",
        "middleware",
        "parent",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        endpoint: Callable[..., Any] = None,
        dependencies: Optional[Dependencies] = None,
        exception_handlers: Optional[ExceptionHandlerMap] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
    ):
        if not path:
            path = "/"
        super().__init__(path=path, endpoint=endpoint)
        self._permissions: Union[List[Permission], VoidType] = Void
        self._dependencies: Dependencies = {}
        self._response_handler: Union[Callable[[Any], Awaitable[StarletteResponse]], VoidType] = (
            Void
        )
        self._interceptors: Union[List[Interceptor], VoidType] = Void
        self.interceptors: Sequence[Interceptor] = []
        self.endpoint = endpoint
        self.parent: ParentType = None
        self.dependencies = dependencies
        self.exception_handlers = exception_handlers
        self.permissions = permissions
        self.middleware = middleware
        self.signature_model: Optional[Type[SignatureModel]] = None
        self.websocket_parameter_model: Optional[TransformerModel] = None
        self.include_in_schema = None
        self.fn: Optional[AnyCallable] = None
        self.tags: Sequence[str] = []

    def validate_reserved_words(self, signature: Signature) -> None:
        """
        Validates if special words are in the signature.
        """
        if signature.return_annotation is not None:
            raise ImproperlyConfigured("Websocket functions should return 'None'.")

        unsupported_kwargs = [REQUEST, DATA, PAYLOAD]
        for kwarg in unsupported_kwargs:
            if kwarg in signature.parameters:
                raise ImproperlyConfigured(
                    f"The '{kwarg}'is not supported with websocket handlers."
                )

    def validate_websocket_handler_function(self) -> None:  # pragma: no cover
        """
        Validates the route handler function once it is set by inspecting its
        return annotations.
        """
        if not self.fn:
            raise ImproperlyConfigured(
                "Cannot call check_handler_function without first setting self.fn"
            )
        signature = Signature.from_callable(self.fn)
        self.validate_reserved_words(signature=signature)

        if SOCKET not in signature.parameters:
            raise ImproperlyConfigured("Websocket handlers must set a 'socket' argument.")
        if not is_async_callable(self.fn):
            raise ImproperlyConfigured(
                "Functions decorated with 'asgi, get, patch, put, post and delete' must be async functions."
            )

    async def handle(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """The handle of a websocket"""
        if self.get_interceptors():
            await self.intercept(scope, receive, send)

        websocket = WebSocket(scope=scope, receive=receive, send=send)
        if self.get_permissions():
            await self.allow_connection(connection=websocket)

        kwargs = await self.get_kwargs(websocket=websocket)

        fn = cast("AsyncAnyCallable", self.fn)
        if isinstance(self.parent, View):
            await fn(self.parent, **kwargs)
        else:
            await fn(**kwargs)

    async def get_kwargs(self, websocket: WebSocket) -> Any:
        """Resolves the required kwargs from the request data.

        Args:
            websocket: WebSocket instance

        Returns:
            Dictionary of parsed kwargs
        """
        assert self.websocket_parameter_model, "handler parameter model not defined."

        signature_model = get_signature(self)
        kwargs = self.websocket_parameter_model.to_kwargs(connection=websocket)
        for dependency in self.websocket_parameter_model.dependencies:
            kwargs[dependency.key] = await self.websocket_parameter_model.get_dependencies(
                dependency=dependency, connection=websocket, **kwargs
            )
        return signature_model.parse_values_for_connection(connection=websocket, **kwargs)


class Include(Mount):
    """
    `Include` object class that allows scalability and modularity
    to happen with elegance.

    Read more about the [Include](https://esmerald.dev/routing/routes/#include) to understand
    what can be done.

    Include manages routes as a list or as a namespace but not both or a
    `ImproperlyConfigured` is raised.
    """

    __slots__ = (
        "path",
        "app",
        "namespace",
        "pattern",
        "name",
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "deprecated",
        "security",
        "tags",
    )

    def __init__(
        self,
        path: Annotated[
            Optional[str],
            Doc(
                """
                Relative path of the `Include`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                Include()
                ```

                **Example with parameters**

                ```python
                Include(path="/{age: int}")
                ```
                """
            ),
        ] = None,
        app: Annotated[
            ASGIApp | str,
            Doc(
                """
                An application can be anything that is treated as an ASGI application.
                For example, it can be a [ChildEsmerald](https://esmerald.dev/routing/router/#child-esmerald-application), another `Esmerald`, a [Router](https://esmerald.dev/routing/router/#router-class) or even an external [WSGI application](https://esmerald.dev/wsgi/) (Django, Flask...)

                The app is a parameter that makes the Include extremely powerful when it comes
                to integrate with ease with whatever Python stack you want and need.

                **Example**

                ```python
                from esmerald import Esmerald, ChildEsmerald, Include

                Esmerald(
                    routes=[
                        Include('/child', app=ChildEsmerald(...))
                    ]
                )
                ```

                **Example with a WSGI framework**

                ```python
                from flask import Flask, escape, request

                from esmerald import Esmerald, Gateway, Include, Request, get
                from esmerald.middleware.wsgi import WSGIMiddleware

                flask_app = Flask(__name__)


                @flask_app.route("/")
                def flask_main():
                    name = request.args.get("name", "Esmerald")
                    return f"Hello, {escape(name)} from your Flask integrated!"


                @get("/home/{name:str}")
                async def home(request: Request) -> dict:
                    name = request.path_params["name"]
                    return {"name": escape(name)}


                app = Esmerald(
                    routes=[
                        Gateway(handler=home),
                        Include("/flask", WSGIMiddleware(flask_app)),
                    ]
                )
                ```

                """
            ),
        ] = None,
        name: Annotated[
            Optional[str],
            Doc(
                """
                The name for the Gateway. The name can be reversed by `url_path_for()`.
                """
            ),
        ] = None,
        routes: Annotated[
            Optional[Sequence[Union[APIGateHandler, Include]]],
            Doc(
                """
                A global `list` of esmerald routes. Those routes may vary and those can
                be `Gateway`, `WebSocketGateWay` or even another `Include`.

                This is also an entry-point for the routes of the Include
                but it **does not rely on only one [level](https://esmerald.dev/application/levels/)**.

                Read more about how to use and leverage
                the [Esmerald routing system](https://esmerald.dev/routing/routes/).

                **Example**

                ```python
                from esmerald import Esmerald, Gateway, Request, get, Include


                @get()
                async def homepage(request: Request) -> str:
                    return "Hello, home!"


                @get()
                async def another(request: Request) -> str:
                    return "Hello, another!"

                app = Esmerald(
                    routes=[
                        Gateway(handler=homepage)
                        Include("/nested", routes=[
                            Gateway(handler=another)
                        ])
                    ]
                )
                ```

                !!! Note
                    The Include is very powerful and this example
                    is not enough to understand what more things you can do.
                    Read in [more detail](https://esmerald.dev/routing/routes/#include) about this.
                """
            ),
        ] = None,
        namespace: Annotated[
            Optional[str],
            Doc(
                """
                A string with a qualified namespace from where the URLs should be loaded.

                The namespace is an alternative to `routes` parameter. When a `namespace` is
                specified and a routes as well, an `ImproperlyCOnfigured` exception is raised as
                it can only be one or another.

                The `namespace` can be extremely useful as it avoids the imports from the top
                of the file that can lead to `partially imported` errors.

                When using a `namespace`, the `Include` will look for the default `route_patterns` list in the imported namespace (object) unless a different `pattern` is specified.

                **Example**

                Assuming there is a file with some routes located at `myapp/auth/urls.py`.

                ```python title="myapp/auth/urls.py"
                from esmerald import Gateway
                from .view import welcome, create_user

                route_patterns = [
                    Gateway(handler=welcome, name="welcome"),
                    Gateway(handler=create_user, name="create-user"),
                ]
                ```

                Using the `namespace` to import the URLs.

                ```python
                from esmerald import Include

                Include("/auth", namespace="myapp.auth.urls")
                ```
                """
            ),
        ] = None,
        pattern: Annotated[
            Optional[str],
            Doc(
                """
                A string `pattern` information from where the urls shall be read from.

                By default, the when using the `namespace` it will lookup for a `route_patterns`
                but somethimes you might want to opt for a different name and this is where the
                `pattern` comes along.

                **Example**

                Assuming there is a file with some routes located at `myapp/auth/urls.py`.
                The urls will be placed inside a `urls` list.

                ```python title="myapp/auth/urls.py"
                from esmerald import Gateway
                from .view import welcome, create_user

                urls = [
                    Gateway(handler=welcome, name="welcome"),
                    Gateway(handler=create_user, name="create-user"),
                ]
                ```

                Using the `namespace` to import the URLs.

                ```python
                from esmerald import Include

                Include("/auth", namespace="myapp.auth.urls", pattern="urls")
                ```
                """
            ),
        ] = None,
        parent: Annotated[
            Optional[ParentType],
            Doc(
                """
                Who owns the Gateway. If not specified, the application automatically it assign it.

                This is directly related with the [application levels](https://esmerald.dev/application/levels/).
                """
            ),
        ] = None,
        dependencies: Annotated[
            Optional[Dependencies],
            Doc(
                """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
            ),
        ] = None,
        interceptors: Annotated[
            Optional[Sequence[Interceptor]],
            Doc(
                """
                A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        permissions: Annotated[
            Optional[Sequence[Permission]],
            Doc(
                """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
            ),
        ] = None,
        exception_handlers: Annotated[
            Optional[ExceptionHandlerMap],
            Doc(
                """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
            ),
        ] = None,
        middleware: Annotated[
            Optional[List[Middleware]],
            Doc(
                """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Starlette Middleware](https://www.starlette.io/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
            ),
        ] = None,
        include_in_schema: Annotated[
            bool,
            Doc(
                """
                Boolean flag indicating if it should be added to the OpenAPI docs.

                This will add all the routes of the Include even those nested (Include containing more Includes.)
                """
            ),
        ] = True,
        deprecated: Annotated[
            Optional[bool],
            Doc(
                """
                Boolean flag for indicating the deprecation of the Include and all of its routes and to display it in the OpenAPI documentation..
                """
            ),
        ] = None,
        security: Annotated[
            Optional[Sequence[SecurityScheme]],
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
        self.path = path
        if not path:
            self.path = "/"

        if namespace and routes:
            raise ImproperlyConfigured("It can only be namespace or routes, not both.")

        if namespace and not isinstance(namespace, str):
            raise ImproperlyConfigured("Namespace must be a string. Example: 'myapp.routes'.")

        if pattern and not isinstance(pattern, str):
            raise ImproperlyConfigured("Pattern must be a string. Example: 'route_patterns'.")

        if pattern and routes:
            raise ImproperlyConfigured("Pattern must be used only with namespace.")

        if namespace:
            routes = include(namespace, pattern)

        self.name = name
        self.namespace = namespace
        self.pattern = pattern
        self.include_in_schema = include_in_schema
        self.dependencies = dependencies or {}
        self.interceptors: Sequence[Interceptor] = interceptors or []
        self.permissions: Sequence[Permission] = permissions or []
        self.middleware = middleware or []
        self.exception_handlers = exception_handlers or {}
        self.deprecated = deprecated
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.parent = parent
        self.security = security or []
        self.tags = tags or []

        if routes:
            routes = self.resolve_route_path_handler(routes)

        # Add the middleware to the include
        include_middleware: Sequence[Middleware] = []

        for _middleware in self.middleware:
            if isinstance(_middleware, StarletteMiddleware):  # pragma: no cover
                include_middleware.append(_middleware)
            else:
                include_middleware.append(  # type: ignore
                    StarletteMiddleware(cast("Type[StarletteMiddleware]", _middleware))
                )

        if isinstance(app, str):
            app = import_string(app)

        self.app = self.resolve_app_parent(app=app)

        super().__init__(
            self.path,
            app=self.app,
            routes=routes,
            name=name,
            middleware=include_middleware,
        )

    def resolve_app_parent(self, app: Optional[Any]) -> Optional[Any]:
        """
        Resolves the owner of ChildEsmerald or Esmerald iself.
        """
        from esmerald import ChildEsmerald, Esmerald

        if app is not None and isinstance(app, (Esmerald, ChildEsmerald)):
            app.parent = self
        return app

    def resolve_route_path_handler(
        self, routes: Sequence[Union[APIGateHandler, Include]]
    ) -> List[Union[Gateway, WebSocketGateway, Include]]:
        """
        Make sure the paths are properly configured from the handler endpoint.
        The handler can be a Starlette function, an View or a HTTPHandler.

        Mount() has a limitation of not allowing nested Mount().

        Example:

            route_patterns = [
                Mount(path='/my path', routes=[
                    Mount(path='/another mount')
                ])
            ]


        Include() extends the Mount and adds extras on the top. Allowing nested
        Include() also allows importing in different ways. Via qualified namespace
        or via list() but not both.

        Example:

            1. Root of the application, example, `urls.py`.

            route_patterns = [
                Include(path='/api/v1/', namespace='myapp.v1.urls'),
                Gateway(path='/example', handler=example_endpoint, name='example')
                ...
            ]

            2. Inside `myapp.v1.urls`

            from mysecondapp.urls import route_patterns

            route_patterns = [
                Include(path='/api/v2/', routes=route_patterns),
                Gateway(path='/another-example', handler=another_endpoint, name='example')
                ...
            ]

            3. Inside `mysecondapp.v1.urls`:

            route_patterns = [
                Gateway(path='/last-example', handler=another_endpoint, name='example')
                ...
            ]

        """
        routing: List[Union[Gateway, WebSocketGateway, Include]] = []

        for route in routes:  # pragma: no cover
            if not isinstance(route, (Include, Gateway, WebSocketGateway)):
                raise ImproperlyConfigured("The route must be of type Gateway or Include")

            route.parent = self
            if isinstance(route, Include):
                routing.append(route)
                continue

            if isinstance(route.handler, (HTTPHandler, WebSocketHandler)):
                route.handler.parent = route
                routing.append(route)
                continue

            if is_class_and_subclass(route.handler, View) or isinstance(route.handler, View):
                if not route.handler.parent:
                    route.handler = route.handler(parent=self)  # type: ignore

                route_handlers: List[
                    Union[HTTPHandler, WebSocketHandler]
                ] = route.handler.get_route_handlers()  # type: ignore[union-attr]

                for route_handler in route_handlers:
                    gateway = (
                        Gateway
                        if not isinstance(route_handler, WebSocketHandler)
                        else WebSocketGateway
                    )
                    gate = gateway(
                        path=route.path,
                        handler=route_handler,
                        name=route_handler.fn.__name__,
                        middleware=route.middleware,
                        interceptors=self.interceptors,
                        permissions=route.permissions,
                        exception_handlers=route.exception_handlers,
                    )

                    if isinstance(gate, Gateway):
                        include_in_schema = (
                            route.include_in_schema
                            if route.include_in_schema is not None
                            else route_handler.include_in_schema
                        )
                        gate.include_in_schema = include_in_schema

                    routing.append(gate)
        return routing
