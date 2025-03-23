from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Type,
    TypeVar,
    Union,
    get_args,
)

# 3rd Party & Framework-Specific Imports
from lilya.middleware import DefineMiddleware
from lilya.types import ASGIApp
from typing_extensions import Literal

from esmerald.background import BackgroundTask, BackgroundTasks
from esmerald.exceptions import MissingDependency
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.router import Include

# Attempt to import optional dependencies, fallback if missing
try:
    from asyncz.schedulers import AsyncIOScheduler
except ImportError:
    AsyncIOScheduler = Any  # type: ignore

try:
    from esmerald.config.template import TemplateConfig
except MissingDependency:
    TemplateConfig = Any  # type: ignore

# TYPE_CHECKING Block - Avoids runtime imports when not needed
if TYPE_CHECKING:
    from esmerald.applications import Application, Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings
    from esmerald.datastructures import Cookie, ResponseHeader, State
    from esmerald.injector import Inject
    from esmerald.protocols.middleware import MiddlewareProtocol
    from esmerald.requests import Request
    from esmerald.responses import Response
    from esmerald.routing.apis.base import View
    from esmerald.routing.gateways import Gateway, WebhookGateway
    from esmerald.routing.router import (
        HTTPHandler,
        Router,
    )
    from esmerald.websockets import WebSocket
else:
    Application = Any
    BaseHTTPMiddleware = Any
    Cookie = Any
    Esmerald = Any
    Gateway = Any
    HTTPHandler = Any
    Inject = Any
    Message = Any
    MiddlewareProtocol = Any
    Receive = Any
    Request = Any
    Response = Any
    ResponseHeader = Any
    Router = Any
    Scope = Any
    Send = Any
    State = Any
    View = Any
    WebSocket = Any
    WebhookGateway = Any

# Type Aliases for Readability
AsyncAnyCallable = Callable[..., Awaitable[Any]]  # Async function returning Any

# HTTP Method Literals
HTTPMethod = Literal["GET", "POST", "DELETE", "PATCH", "PUT", "HEAD"]
HTTPMethods = get_args(HTTPMethod)

# Middleware Type Alias
Middleware = DefineMiddleware

# Response & Exception Handling Types
ResponseType = Type[Response]
ResponseHeaders = Dict[str, ResponseHeader]
ResponseCookies = List[Cookie]
ExceptionType = TypeVar("ExceptionType", bound=Exception)
ExceptionHandler = Callable[[Request, ExceptionType], Response]
ExceptionHandlerMap = Mapping[Union[int, Type[Exception]], ExceptionHandler]

# Reserved Keyword Arguments for Handlers
_ReservedKwargs = Literal[
    "request", "socket", "headers", "query", "cookies", "state", "data", "payload"
]
ReservedKwargs = get_args(_ReservedKwargs)

# Scheduler Type
SchedulerType = AsyncIOScheduler
DatetimeType = TypeVar("DatetimeType", bound=datetime)

# Parent Type for Various Routing Components
ParentType = Union[View, Router, Gateway, WebSocketGateway, Esmerald, Include, Application]

# API Handler for Gateways
APIGateHandler = Union[Gateway, WebSocketGateway]

# Route Parent Types
RouteParent = Union[
    "Router", "Include", "ASGIApp", "Gateway", "WebSocketGateway", "WebhookGateway"
]

# Background Task Types
BackgroundTaskType = Union[BackgroundTask, BackgroundTasks]

# Security Scheme Definition
SecurityScheme = Dict[str, List[str]]

# General Connection Type (Request or WebSocket)
ConnectionType = Union["Request", "WebSocket"]

# Common Dictionary Type Aliases
DictStr = Dict[str, str]
DictAny = Dict[str, Any]

# API Settings Type
SettingsType = Type["EsmeraldAPISettings"]

# Lifespan Handler Type
LifeSpanHandler = Union[Callable[[], None], Callable[[], Awaitable[None]]]
