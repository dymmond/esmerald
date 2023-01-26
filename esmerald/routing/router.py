import inspect
from copy import copy
from enum import Enum, IntEnum
from inspect import Signature
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from starlette import status
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse
from starlette.responses import Response as StarletteResponse
from starlette.routing import BaseRoute as StarletteBaseRoute
from starlette.routing import Host, Mount, NoMatchFound
from starlette.routing import Route as StarletteRoute
from starlette.routing import Router as StarletteRouter
from starlette.routing import WebSocketRoute as StarletteWebSocketRoute
from starlette.routing import compile_path
from starlette.types import ASGIApp, Receive, Scope, Send

from esmerald.conf import settings
from esmerald.datastructures import File, Redirect, URLPath
from esmerald.enums import HttpMethod, MediaType
from esmerald.exceptions import (
    ImproperlyConfigured,
    MethodNotAllowed,
    NotFound,
    ValidationErrorException,
)
from esmerald.injector import Inject
from esmerald.interceptors.types import Interceptor
from esmerald.openapi.datastructures import ResponseSpecification
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing.base import BaseHandlerMixin
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.views import APIView
from esmerald.transformers.datastructures import EsmeraldSignature as SignatureModel
from esmerald.transformers.model import TransformerModel
from esmerald.transformers.utils import get_signature
from esmerald.typing import Void, VoidType
from esmerald.urls import include
from esmerald.utils.constants import DATA, REDIRECT_STATUS_CODES, REQUEST, SOCKET
from esmerald.utils.helpers import is_async_callable, is_class_and_subclass
from esmerald.utils.url import clean_path
from esmerald.websockets import WebSocket, WebSocketClose

if TYPE_CHECKING:
    from openapi_schemas_pydantic.v3_1_0 import SecurityRequirement
    from pydantic.typing import AnyCallable

    from esmerald.applications import Esmerald
    from esmerald.exceptions import HTTPException
    from esmerald.permissions.types import Permission
    from esmerald.types import (
        APIGateHandler,
        AsyncAnyCallable,
        BackgroundTaskType,
        CoroutineHandler,
        Dependencies,
        ExceptionHandler,
        ExceptionHandlers,
        HTTPMethod,
        LifeSpanHandler,
        Middleware,
        ParentType,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
        RouteParent,
    )


class Parent:
    def create_signature_models(self, route: "RouteParent"):
        """
        Creates the signature models for the given routes.

        Args:
            route: The route for the signature model to be created.
        """
        if isinstance(route, (Include, Host)):
            for _route in route.routes:
                self.create_signature_models(_route)

        if isinstance(route, Gateway):
            if not route.handler.parent:
                route.handler.parent = route

            if not is_class_and_subclass(route.handler, APIView) and not isinstance(
                route.handler, APIView
            ):
                route.handler.create_signature_model()

        if isinstance(route, WebSocketGateway):
            route.handler.create_signature_model(is_websocket=True)

    def validate_root_route_parent(
        self,
        value: Union["Router", "Include", "ASGIApp", "Gateway", "WebSocketGateway"],
        override: bool = False,
    ):
        """
        Handles everything parent from the root. When in the root, the parent must be setup.
        Appends the route path if exists.
        """
        # Getting the value of the router for the path
        value.path = clean_path(self.path + getattr(value, "path", "/"))
        if isinstance(value, (Include, Gateway, WebSocketGateway)):
            if not value.parent and not override:
                value.parent = self

        if isinstance(value, (Gateway, WebSocketGateway)):
            if not is_class_and_subclass(value.handler, APIView) and not isinstance(
                value.handler, APIView
            ):
                if not value.handler.parent:
                    value.handler.parent = value
            else:
                if not value.handler.parent:
                    value(parent=self)

                route_handlers = value.handler.get_route_handlers()
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

                    if isinstance(gate, Gateway):
                        include_in_schema = (
                            value.include_in_schema
                            if value.include_in_schema is not None
                            else route_handler.include_in_schema
                        )
                        gate.include_in_schema = include_in_schema

                    self.routes.append(gate)
                self.routes.pop(self.routes.index(value))


class Router(StarletteRouter, Parent):
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
    )

    def __init__(
        self,
        path: Optional[str] = None,
        app: Optional["Esmerald"] = None,
        parent: Optional["Router"] = None,
        on_shutdown: Optional[List["LifeSpanHandler"]] = None,
        on_startup: Optional[List["LifeSpanHandler"]] = None,
        redirect_slashes: bool = True,
        default: Optional["ASGIApp"] = None,
        routes: Optional[List[Union["APIGateHandler", "Include"]]] = None,
        name: Optional[str] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        interceptors: Optional[List["Interceptor"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        response_class: Optional["ResponseType"] = None,
        response_cookies: Optional["ResponseCookies"] = None,
        response_headers: Optional["ResponseHeaders"] = None,
        lifespan: Optional[Callable[["Esmerald"], AsyncContextManager]] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
    ):
        self.app = app
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
            ):
                raise ImproperlyConfigured(f"The route {route} must be of type Gateway or Include")
        routes = routes or []
        super().__init__(
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            redirect_slashes=redirect_slashes,
            routes=routes,
            default=default,
            lifespan=lifespan,
        )
        self.path = path
        self.parent: Optional["Router"] = parent or self.app
        self.dependencies = dependencies or {}
        self.exception_handlers = exception_handlers or {}
        self.interceptors = interceptors or []
        self.permissions = permissions or []
        self.middleware = middleware or []
        self.routes = routes
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

    def reorder_routes(self):
        return sorted(
            self.routes,
            key=lambda router: router.path != "" and router.path != "/",
            reverse=True,
        )

    def activate(self):
        self.routes = self.reorder_routes()

    def add_apiview(self, value: Type["APIView"]):
        routes = []
        if not value.handler.parent:
            value(parent=self)

        route_handlers = value.handler.get_route_handlers()
        for route_handler in route_handlers:
            gateway = (
                Gateway if not isinstance(route_handler, WebSocketHandler) else WebSocketGateway
            )
            gate = gateway(
                path=value.path,
                handler=route_handler,
                name=route_handler.path,
                middleware=value.middleware,
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
        path: str,
        handler: Type["HTTPHandler"],
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        interceptors: Optional[List["Interceptor"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
        deprecated: Optional[bool] = None,
    ) -> None:
        """
        Adds a new route on a router level making it dynamic based on the handler given.
        If methods is passed, then a new handler will be created for each method passed.
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
            exception_handlers=exception_handlers,
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
        path: str,
        handler: Type["WebSocketHandler"],
        name: Optional[str] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        interceptors: Optional[List["Interceptor"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
    ) -> None:
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

    async def not_found(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
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
                return route.url_path_for(name, **path_params)
            except NoMatchFound:
                pass

            if isinstance(route, (Gateway, WebSocketGateway)):
                try:
                    return route.handler.url_path_for(name, **path_params)
                except NoMatchFound:
                    pass

        raise NoMatchFound(name, path_params)


class HTTPHandler(BaseHandlerMixin, StarletteRoute):
    __slots__ = (
        "path",
        "_permissions",
        "_dependencies",
        "_response_handler",
        "methods",
        "status_code",
        "content_encoding",
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
        "raise_exceptions",
    )

    def __init__(
        self,
        path: Optional[str] = None,
        endpoint: Callable[..., "CoroutineHandler"] = None,
        *,
        methods: Optional[List["HTTPMethod"]] = None,
        status_code: Optional[int] = None,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional["ResponseType"] = None,
        response_cookies: Optional["ResponseCookies"] = None,
        response_headers: Optional["ResponseHeaders"] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        response_description: Optional[str] = "Successful Response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
    ) -> None:
        if not path:
            path = "/"
        super().__init__(path=path, endpoint=endpoint, include_in_schema=include_in_schema)
        """
        Handles the "handler" or "apiview" of the platform. A handler can be any get, put, patch, post, delete or route.
        """
        self._permissions: Union[List["Permission"], "VoidType"] = Void
        self._dependencies: Union[Dict[str, Inject], "VoidType"] = Void
        self._response_handler: Union[
            "Callable[[Any], Awaitable[StarletteResponse]]", VoidType
        ] = Void

        self.parent: "ParentType" = None
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
        if HttpMethod.GET in methods:
            self.methods.add(HttpMethod.HEAD.value)

        if isinstance(status_code, IntEnum):
            status_code = int(status_code)
        self.status_code = status_code

        self.exception_handlers = exception_handlers or {}
        self.dependencies = dependencies or {}
        self.description = description or inspect.cleandoc(self.endpoint.__doc__ or "")
        self.permissions = list(permissions) if permissions else []
        self.middleware = list(middleware) if middleware else []
        self.description = self.description.split("\f")[0]
        self.media_type = media_type
        self.response_class = response_class
        self.response_cookies = response_cookies
        self.response_headers = response_headers
        self.background = background
        self.signature_model: Optional[Type["SignatureModel"]] = None
        self.transformer: Optional["TransformerModel"] = None
        self.response_description = response_description
        self.responses = responses or {}
        self.content_encoding = content_encoding
        self.content_media_type = content_media_type
        self.raise_exceptions = raise_exceptions

        self.fn: Optional["AnyCallable"] = None
        self.app: Optional["ASGIApp"] = None
        self.route_map: Dict["HTTPMethod" : Tuple["HTTPHandler", "TransformerModel"]] = {}
        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

    @property
    def http_methods(self) -> List[str]:
        """
        Converts the methods set into a list of methods.
        """
        return [method for method in self.methods]

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
    def allow_header(self):
        """
        Default allow header to be injected in the Response and Starlette Response type
        handlers.
        """
        return {"allow": str(self.methods)}

    @property
    def permission_names(self):
        """
        List of permissions for the route. This is used for OpenAPI Spec purposes only.
        """
        return [permission.__name__ for permission in self.permissions]

    def get_response_class(self) -> Type["Response"]:
        """
        Returns the closest custom Response class in the parent graph or the
        default Response class.
        """
        response_class = Response
        for layer in self.parent_levels:
            if layer.response_class is not None:
                response_class = layer.response_class
        return response_class

    def get_response_headers(self) -> "ResponseHeaders":
        """
        Returns all header parameters in the scope of the handler function.
        """
        resolved_response_headers = {}
        for layer in self.parent_levels:
            resolved_response_headers.update(layer.response_headers or {})
        return resolved_response_headers

    def get_response_cookies(self) -> "ResponseCookies":
        """Returns a list of Cookie instances. Filters the list to ensure each
        cookie key is unique.
        """

        cookies: "ResponseCookies" = []
        for layer in self.parent_levels:
            cookies.extend(layer.response_cookies or [])
        filtered_cookies: "ResponseCookies" = []
        for cookie in reversed(cookies):
            if not any(cookie.key == c.key for c in filtered_cookies):
                filtered_cookies.append(cookie)
        return filtered_cookies

    async def handle(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        ASGIapp that authorizes the connection and then awaits the handler function.
        """
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

    def __call__(self, fn: "AnyCallable") -> "ASGIApp":
        self.fn = fn
        self.endpoint = fn
        self.validate_handler()
        return self

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

        if not settings.enable_sync_handlers:
            fn = cast("AnyCallable", self.fn)
            if not is_async_callable(fn):
                raise ImproperlyConfigured(
                    "Functions decorated with 'route, websocket, get, patch, put, post and delete' must be async functions"
                )

    def validate_annotations(self):
        """
        Validate annotations of the handlers.
        """
        return_annotation = self.signature.return_annotation

        if return_annotation is Signature.empty:
            raise ImproperlyConfigured(
                "A return value of a route handler function should be type annotated."
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

    def validate_reserved_kwargs(self):
        """
        Validates if special words are in the signature.
        """
        if DATA in self.signature.parameters and "GET" in self.methods:
            raise ImproperlyConfigured("'data' argument is unsupported for 'GET' request handlers")

        if SOCKET in self.signature.parameters:
            raise ImproperlyConfigured("The 'socket' argument is not supported with http handlers")

    def validate_handler(self):
        self.check_handler_function()
        self.validate_annotations()
        self.validate_reserved_kwargs()

    async def to_response(self, app: "Esmerald", data: Any) -> StarletteResponse:
        response_handler = self.get_response_handler()
        return await response_handler(app=app, data=data)


class WebSocketHandler(BaseHandlerMixin, StarletteWebSocketRoute):
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
        path: Union[Optional[str], Optional[List[str]]] = None,
        *,
        endpoint: Callable[..., "CoroutineHandler"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], "ExceptionHandler"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
    ):
        if not path:
            path = "/"
        super().__init__(path=path, endpoint=endpoint)
        self._permissions: Union[List["Permission"], "VoidType"] = Void
        self._dependencies: Union[Dict[str, Inject], "VoidType"] = Void
        self._response_handler: Union[
            "Callable[[Any], Awaitable[StarletteResponse]]", VoidType
        ] = Void

        self.parent: "ParentType" = None
        self.dependencies = dependencies
        self.exception_handlers = exception_handlers
        self.permissions = permissions
        self.middleware = middleware
        self.signature_model: Optional[Type["SignatureModel"]] = None
        self.websocket_parameter_model: Optional["TransformerModel"] = None

    def __call__(self, fn: "AnyCallable") -> "ASGIApp":
        self.fn = fn
        self.endpoint = fn
        self.validate_websocket_handler_function()
        return self

    def validate_reserved_words(self, signature: "Signature"):
        """
        Validates if special words are in the signature.
        """
        if signature.return_annotation is not None:
            raise ImproperlyConfigured("Websocket functions should return 'None'.")

        unsupported_kwargs = [REQUEST, DATA]
        for kwarg in unsupported_kwargs:
            if kwarg in signature.parameters:
                raise ImproperlyConfigured(
                    f"The '{kwarg}'is not supported with websocket handlers."
                )

    def validate_websocket_handler_function(self) -> None:
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
        websocket = WebSocket[Any, Any](scope=scope, receive=receive, send=send)
        if self.get_permissions():
            await self.allow_connection(connection=websocket)

        kwargs = await self.get_kwargs(websocket=websocket)

        fn = cast("AsyncAnyCallable", self.fn)
        if isinstance(self.parent, APIView):
            await fn(self.parent, **kwargs)
        else:
            await fn(**kwargs)

    async def get_kwargs(self, websocket: WebSocket[Any, Any]) -> Dict[str, Any]:
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
    Esmerald version of the classic mount from Starlette but extends it further
    to contemplate the includes.

    Handle with specific includes from the URLs.

    Include manages routes as a list or as a namespace but not both or a
    ImproperlyConfigured is raised.

    If the app is an Esmerald or ChildEsmerald, then the parent is set to be the include
    itself.
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
    )

    def __init__(
        self,
        path: Optional[str] = None,
        app: Optional["ASGIApp"] = None,
        name: Optional[str] = None,
        routes: Optional[List[StarletteBaseRoute]] = None,
        namespace: Optional[str] = None,
        pattern: Optional[str] = None,
        parent: Optional["Router"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], "ExceptionHandler"]] = None,
        interceptors: Optional[List["Interceptor"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        include_in_schema: Optional[bool] = True,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
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
            routes: List["APIGateHandler"] = include(namespace, pattern)

        self.app = app
        self.name = name
        self.namespace = namespace
        self.pattern = pattern
        self.include_in_schema = include_in_schema
        self.dependencies = dependencies or {}
        self.interceptors = interceptors or []
        self.permissions = permissions or []
        self.middleware = middleware or []
        self.exception_handlers = exception_handlers or {}
        self.deprecated = deprecated
        self.response_class = None
        self.response_cookies = None
        self.response_headers = None
        self.parent = parent
        self.security = security or []

        if routes:
            routes = self.resolve_route_path_handler(routes)

        # Build the middleware from the routes
        routes_middleware = []
        for route in routes or []:
            routes_middleware = self.build_routes_middleware(route)

        # Add the middleware to the include
        self.middleware += routes_middleware
        include_middleware = []

        if self.middleware:
            for middleware in self.middleware:
                if isinstance(middleware, StarletteMiddleware):
                    include_middleware.append(middleware)
                else:
                    include_middleware.append(StarletteMiddleware(middleware))

        super().__init__(
            self.path, app=self.app, routes=routes, name=name, middleware=include_middleware
        )

        self.path_regex, self.path_format, self.param_convertors = compile_path(
            self.path + "/{path:path}"
        )

    def build_routes_middleware(
        self, route: "RouteParent", middlewares: Optional[List["Middleware"]] = None
    ):
        """
        Builds the middleware stack from the top to the bottom of the routes.
        """
        from esmerald import ChildEsmerald, Esmerald

        if not middlewares:
            middlewares = []

        if isinstance(route, Include):
            app = getattr(route, "app", None)
            if app and isinstance(app, (Esmerald, ChildEsmerald)):
                return middlewares

        if isinstance(route, (Gateway, WebSocketGateway)):
            middlewares.extend(route.middleware)
            if route.handler.middleware:
                middlewares.extend(route.handler.middleware)

        return middlewares

    def resolve_route_path_handler(self, routes: List[StarletteBaseRoute]):
        """
        Make sure the paths are properly configured from the handler endpoint.
        The handler can be a Starlette function, an APIView or a HTTPHandler.

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
        routing = []

        for route in routes:
            if not isinstance(route, (Include, Gateway, WebSocketGateway, Mount)):
                raise ImproperlyConfigured("The route must be of type Gateway or Include")
            route.parent = self
            if isinstance(route, Include):
                routing.append(route)
            else:
                if isinstance(route.handler, (HTTPHandler, WebSocketHandler)):
                    route.handler.parent = route
                    routing.append(route)
                    continue

                if is_class_and_subclass(route.handler, APIView) or isinstance(
                    route.handler, APIView
                ):
                    if not route.handler.parent:
                        route.handler = route.handler(parent=self)
                    route_handlers = route.handler.get_route_handlers()

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
