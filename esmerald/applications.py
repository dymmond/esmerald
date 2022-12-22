from datetime import timezone
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Union,
)

from asyncz.contrib.esmerald.scheduler import EsmeraldScheduler
from esmerald.conf import settings
from esmerald.config import CORSConfig, CSRFConfig, SessionConfig, TemplateConfig
from esmerald.config.openapi import OpenAPIConfig
from esmerald.config.static_files import StaticFilesConfig
from esmerald.datastructures import State
from esmerald.exception_handlers import (
    improperly_configured_exception_handler,
    validation_error_exception_handler,
)
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.middleware.asyncexitstack import AsyncExitStackMiddleware
from esmerald.middleware.cors import CORSMiddleware
from esmerald.middleware.csrf import CSRFMiddleware
from esmerald.middleware.exceptions import (
    EsmeraldAPIExceptionMiddleware,
    ExceptionMiddleware,
)
from esmerald.middleware.sessions import SessionMiddleware
from esmerald.middleware.trustedhost import TrustedHostMiddleware
from esmerald.permissions.types import Permission
from esmerald.protocols.template import TemplateEngineProtocol
from esmerald.routing import gateways
from esmerald.routing.router import HTTPHandler, Include, Router, WebSocketHandler
from esmerald.types import (
    APIGateHandler,
    ASGIApp,
    Dependencies,
    ExceptionHandlers,
    LifeSpanHandler,
    Middleware,
    ParentType,
    Receive,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
    RouteParent,
    SchedulerType,
    Scope,
    Send,
)
from openapi_schemas_pydantic.v3_1_0 import License, SecurityRequirement, Server
from openapi_schemas_pydantic.v3_1_0.open_api import OpenAPI
from starlette.applications import Starlette
from starlette.middleware import Middleware as StarletteMiddleware  # noqa

if TYPE_CHECKING:
    from openapi_schemas_pydantic.v3_1_0 import SecurityRequirement


class Esmerald(Starlette):
    """
    Creates a Esmerald application instance.
    """

    __slots__ = (
        "title",
        "app_name",
        "description",
        "version",
        "contact",
        "terms_of_service",
        "license",
        "servers",
        "secret",
        "allowed_hosts",
        "allow_origins",
        "permissions",
        "dependencies",
        "middleware",
        "exception_handlers",
        "csrf_config",
        "openapi_config",
        "cors_config",
        "static_files_config",
        "template_config",
        "session_config",
        "response_class",
        "response_cookies",
        "response_headers",
        "scheduler_class",
        "scheduler",
        "tags",
        "root_path",
        "deprecated",
        "security",
        "include_in_schema",
        "redirect_slashes",
    )

    def __init__(
        self,
        *,
        debug: bool = settings.debug,
        title: Optional[str] = settings.title,
        version: Optional[str] = settings.version,
        summary: Optional[str] = settings.summary,
        app_name: Optional[str] = settings.app_name,
        description: Optional[str] = settings.description,
        contact: Optional[Dict[str, Union[str, Any]]] = settings.contact,
        terms_of_service: Optional[str] = settings.terms_of_service,
        license: Optional[License] = None,
        security: Optional[List[SecurityRequirement]] = None,
        servers: List[Server] = [Server(url="/")],
        secret_key: Optional[str] = settings.secret_key,
        allowed_hosts: Optional[List[str]] = settings.allowed_hosts,
        allow_origins: Optional[List[str]] = settings.allow_origins,
        permissions: Optional[List["Permission"]] = settings.permissions,
        dependencies: Optional["Dependencies"] = settings.dependencies,
        csrf_config: Optional["CSRFConfig"] = settings.csrf_config,
        openapi_config: Optional["OpenAPIConfig"] = settings.openapi_config,
        cors_config: Optional["CORSConfig"] = settings.cors_config,
        static_files_config: Optional["StaticFilesConfig"] = settings.static_files_config,
        template_config: Optional["TemplateConfig"] = settings.template_config,
        session_config: Optional["SessionConfig"] = settings.session_config,
        response_class: Optional["ResponseType"] = settings.response_class,
        response_cookies: Optional["ResponseCookies"] = settings.response_cookies,
        response_headers: Optional["ResponseHeaders"] = settings.response_headers,
        scheduler_class: Optional["SchedulerType"] = settings.scheduler_class,
        scheduler_tasks: Optional[Dict[str, str]] = settings.scheduler_tasks,
        scheduler_configurations: Optional[
            Dict[str, Union[str, Dict[str, str]]]
        ] = settings.scheduler_configurations,
        enable_scheduler: bool = settings.enable_scheduler,
        timezone: Optional[timezone] = settings.timezone,
        routes: Optional[List["APIGateHandler"]] = settings.routes,
        root_path: str = settings.root_path,
        middleware: Optional[Sequence["Middleware"]] = settings.middleware,
        exception_handlers: Optional["ExceptionHandlers"] = settings.exception_handlers,
        on_shutdown: Optional[List["LifeSpanHandler"]] = settings.on_shutdown,
        on_startup: Optional[List["LifeSpanHandler"]] = settings.on_startup,
        lifespan: Optional[Callable[["Esmerald"], "AsyncContextManager"]] = settings.lifespan,
        tags: Optional[List[str]] = settings.tags,
        include_in_schema: bool = settings.include_in_schema,
        deprecated: Optional[bool] = None,
        enable_openapi: bool = settings.enable_openapi,
        redirect_slashes: bool = settings.redirect_slashes,
    ) -> None:

        assert lifespan is None or (
            on_startup is None and on_shutdown is None
        ), "Use either 'lifespan' or 'on_startup'/'on_shutdown', not both."

        if allow_origins and cors_config:
            raise ImproperlyConfigured("It can be only allow_origins or cors_config but not both.")

        self._debug = debug
        self.title = title
        self.name = app_name
        self.description = description
        self.version = version
        self.summary = summary
        self.contact = contact
        self.terms_of_service = terms_of_service
        self.license_info = license
        self.servers = servers
        self.secret_key = secret_key
        self.allowed_hosts = allowed_hosts
        self.allow_origins = allow_origins
        self.dependencies = dependencies or {}
        self.permissions = permissions or []
        self.csrf_config = csrf_config
        self.cors_config = cors_config
        self.openapi_config = openapi_config
        self.openapi_schema: Optional["OpenAPI"] = None
        self.template_config = template_config
        self.static_files_config = static_files_config
        self.session_config = session_config
        self.response_class = response_class
        self.response_cookies = response_cookies
        self.response_headers = response_headers
        self.scheduler_class = scheduler_class
        self.scheduler_tasks = scheduler_tasks or {}
        self.scheduler_configurations = scheduler_configurations or {}
        self.enable_scheduler = enable_scheduler
        self.timezone = timezone
        self.tags = tags
        self.include_in_schema = include_in_schema
        self.middleware = middleware or []

        self.state = State()
        self.async_exit_config = settings.async_exit_config
        self.root_path = root_path
        self.parent: Optional[Union["ParentType", "Esmerald", "ChildEsmerald"]] = None
        self.on_shutdown = on_shutdown
        self.on_startup = on_startup
        self.security = security
        self.enable_openapi = enable_openapi
        self.redirect_slashes = redirect_slashes

        self.router: "Router" = Router(
            on_shutdown=on_shutdown,
            on_startup=on_startup,
            routes=routes,
            app=self,
            lifespan=lifespan,
            deprecated=deprecated,
            security=security,
            redirect_slashes=self.redirect_slashes,
        )

        self.exception_handlers = {} if exception_handlers is None else dict(exception_handlers)
        self.get_default_exception_handlers()

        self.user_middleware = self.build_user_middleware_stack()
        self.middleware_stack = self.build_middleware_stack()
        self.template_engine = self.get_template_engine(self.template_config)

        if self.static_files_config:
            for config in (
                self.static_files_config
                if isinstance(self.static_files_config, list)
                else [self.static_files_config]
            ):
                static_route = Include(path=config.path, app=config.to_app())
                self.router.validate_root_route_parent(static_route)
                self.router.routes.append(static_route)

        if self.enable_scheduler:
            self.scheduler = EsmeraldScheduler(
                app=self,
                scheduler_class=self.scheduler_class,
                tasks=self.scheduler_tasks,
                timezone=self.timezone,
                configurations=self.scheduler_configurations,
            )

        self.activate_openapi()

    def activate_openapi(self) -> None:
        if self.openapi_config and self.enable_openapi:
            self.openapi_schema = self.openapi_config.create_openapi_schema_model(self)
            gateway = gateways.Gateway(handler=self.openapi_config.openapi_apiview)
            self.router.add_apiview(value=gateway)

    def get_template_engine(
        self, template_config: "TemplateConfig"
    ) -> Optional["TemplateEngineProtocol"]:
        """
        Returns the template engine for the application.
        """
        if not template_config:
            return

        engine = template_config.engine(template_config.directory)
        return engine

    def add_route(
        self,
        path: str,
        handler: "HTTPHandler",
        router: Optional["Router"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> None:
        router = router or self.router
        route = router.add_route(
            path=path,
            handler=handler,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            name=name,
            include_in_schema=include_in_schema,
        )

        self.activate_openapi()
        return route

    def add_websocket_route(
        self,
        path: str,
        handler: "HTTPHandler",
        router: Optional["Router"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional["ExceptionHandlers"] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
        name: Optional[str] = None,
    ) -> None:
        router = router or self.router
        return router.add_websocket_route(
            path=path,
            handler=handler,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            name=name,
        )

    def add_router(self, router: "Router"):
        """
        Adds a router to the application.
        """
        for route in router.routes:
            if isinstance(route, Include):
                self.router.routes.append(
                    Include(
                        path=route.path,
                        app=route.app,
                        dependencies=route.dependencies,
                        exception_handlers=route.exception_handlers,
                        name=route.name,
                        middleware=route.middleware,
                        permissions=route.permissions,
                        routes=route.routes,
                        parent=self.router,
                    )
                )
                continue

            gateway = (
                gateways.Gateway
                if not isinstance(route.handler, WebSocketHandler)
                else gateways.WebSocketGateway
            )

            if self.on_startup:
                self.on_startup.extend(router.on_startup)
            if self.on_shutdown:
                self.on_shutdown.extend(router.on_shutdown)

            self.router.routes.append(
                gateway(
                    path=route.path,
                    dependencies=route.dependencies,
                    exception_handlers=route.exception_handlers,
                    name=route.name,
                    middleware=route.middleware,
                    permissions=route.permissions,
                    handler=route.handler,
                    parent=self.router,
                    is_from_router=True,
                )
            )

        self.activate_openapi()

    def get_default_exception_handlers(self) -> None:
        """
        Default exception handlers added to the application.
        Defaulting the HTTPException and ValidationError handlers to JSONResponse.

        The values can be overritten by calling the self.add_event_handler().

        Example:
            app = Esmerald()

            app.add_event_handler(HTTPException, my_new_handler)
            app.add_event_handler(ValidationError, my_new_422_handler)

        """
        self.exception_handlers.setdefault(
            ImproperlyConfigured, improperly_configured_exception_handler
        )
        self.exception_handlers.setdefault(
            ValidationErrorException, validation_error_exception_handler
        )

    def build_routes_middleware(
        self, route: "RouteParent", middlewares: Optional[List["Middleware"]] = None
    ):
        """
        Builds the middleware stack from the top to the bottom of the routes.
        We need to make sure the Esmerald/ChildEsmerald app.
        """
        if not middlewares:
            middlewares = []

        if isinstance(route, Include):
            app = getattr(route, "app", None)
            if app and isinstance(app, (Esmerald, ChildEsmerald)):
                return middlewares

            middlewares.extend(route.middleware)
            for _route in route.routes:
                middlewares = self.build_routes_middleware(_route, middlewares)

        if isinstance(route, (gateways.Gateway, gateways.WebSocketGateway)):
            middlewares.extend(route.middleware)
            if route.handler.middleware:
                middlewares.extend(route.handler.middleware)

        return middlewares

    def build_routes_exception_handlers(
        self,
        route: "RouteParent",
        exception_handlers: Optional["ExceptionHandlers"] = None,
    ):
        """
        Builds the exception handlers stack from the top to the bottom of the routes.
        """
        if not exception_handlers:
            exception_handlers = {}

        if isinstance(route, Include):
            exception_handlers.update(route.exception_handlers)
            app = getattr(route, "app", None)
            if app and isinstance(app, (Esmerald, ChildEsmerald)):
                return exception_handlers

            for _route in route.routes:
                exception_handlers = self.build_routes_exception_handlers(
                    _route, exception_handlers
                )

        if isinstance(route, (gateways.Gateway, gateways.WebSocketGateway)):
            exception_handlers.update(route.exception_handlers)
            if route.handler.exception_handlers:
                exception_handlers.update(route.handler.exception_handlers)

        return exception_handlers

    def build_user_middleware_stack(self) -> List["StarletteMiddleware"]:
        """
        Configures all the passed settings
        and wraps inside an exception handler.

        CORS, CSRF, TrustedHost and JWT are provided to the __init__ they will wapr the
        handler as well.

        It evaluates the middleware passed into the routes from bottom up
        """
        user_middleware = []
        handlers_middleware = []

        if self.allowed_hosts:
            user_middleware.append(
                StarletteMiddleware(TrustedHostMiddleware, allowed_hosts=self.allowed_hosts)
            )
        if self.cors_config:
            user_middleware.append(StarletteMiddleware(CORSMiddleware, **self.cors_config.dict()))
        if self.csrf_config:
            user_middleware.append(StarletteMiddleware(CSRFMiddleware, config=self.csrf_config))

        if self.session_config:
            user_middleware.append(
                StarletteMiddleware(SessionMiddleware, **self.session_config.dict())
            )

        handlers_middleware += self.router.middleware
        for route in self.routes or []:
            handlers_middleware.extend(self.build_routes_middleware(route))

        self.middleware += handlers_middleware

        for middleware in self.middleware or []:
            if isinstance(middleware, StarletteMiddleware):
                user_middleware.append(middleware)
            else:
                user_middleware.append(StarletteMiddleware(middleware))
        return user_middleware

    def build_middleware_stack(self) -> "ASGIApp":
        """
        Esmerald uses the [esmerald.protocols.MiddlewareProtocol] (interfaces) and therefore we
        wrap the StarletteMiddleware in a slighly different manner.

        Overriding the default build_middleware_stack will allow to control the initial
        middlewares that are loaded by Esmerald. All of these values can be updated.

        For each route, it will verify from top to bottom which exception handlers are being passed
        and called them accordingly.

        For APIViews, since it's a "wrapper", the handler will update the current list to contain
        both.
        """
        debug = self.debug
        error_handler = None
        exception_handlers = {}

        for key, value in self.exception_handlers.items():
            if key in (500, Exception):
                error_handler = value
            else:
                exception_handlers[key] = value

        for route in self.routes or []:
            exception_handlers.update(self.build_routes_exception_handlers(route))

        middleware = (
            [
                StarletteMiddleware(
                    EsmeraldAPIExceptionMiddleware,
                    exception_handlers=exception_handlers,
                    error_handler=error_handler,
                    debug=debug,
                ),
            ]
            + self.user_middleware
            + [
                StarletteMiddleware(
                    ExceptionMiddleware,
                    handlers=exception_handlers,
                    debug=debug,
                ),
                StarletteMiddleware(AsyncExitStackMiddleware, config=self.async_exit_config),
            ]
        )

        app: "ASGIApp" = self.router
        for cls, options in reversed(middleware):
            app = cls(app=app, **options)

        return app

    @property
    def settings(self) -> settings:
        """
        Returns the Esmerald settings object for easy access.
        """
        return settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        if scope["type"] == "lifespan":
            await self.router.lifespan(scope, receive, send)
            return
        if self.root_path:
            scope["root_path"] = self.root_path
        scope["state"] = {}
        await super().__call__(scope, receive, send)

    def mount(self, path: str, app: ASGIApp, name: Optional[str] = None) -> None:
        raise ImproperlyConfigured("`mount` is not supported by Esmerald. Use Include() instead.")

    def host(self, host: str, app: ASGIApp, name: Optional[str] = None) -> None:
        raise ImproperlyConfigured(
            "`host` is not supported by Esmerald. Use Starlette Host() instead."
        )

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        include_in_schema: bool = True,
    ) -> Callable:
        raise ImproperlyConfigured("`route` is not valid. Use Gateway instead.")

    def websocket_route(self, path: str, name: Optional[str] = None) -> Callable:
        raise ImproperlyConfigured("`websocket_route` is not valid. Use WebSocketGateway instead.")


class ChildEsmerald(Esmerald):
    """
    A simple visual representation of an Esmerald application, exactly like Esmerald
    but for organisation purposes it might be preferred to use this class.
    """

    ...
