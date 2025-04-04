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

from lilya.middleware import DefineMiddleware
from lilya.types import ASGIApp
from typing_extensions import Literal

from esmerald.background import BackgroundTask, BackgroundTasks
from esmerald.exceptions import MissingDependency
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.router import Include

try:
    from asyncz.schedulers import AsyncIOScheduler
except ImportError:
    AsyncIOScheduler = Any  # type: ignore

try:
    from esmerald.core.config.template import TemplateConfig as TemplateConfig
except MissingDependency:
    TemplateConfig = Any  # type: ignore

if TYPE_CHECKING:
    from esmerald.applications import Application, Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings  # noqa
    from esmerald.core.datastructures import Cookie, ResponseHeader
    from esmerald.injector import Inject
    from esmerald.requests import Request
    from esmerald.responses import Response
    from esmerald.routing.apis.base import View
    from esmerald.routing.gateways import Gateway, WebhookGateway  # noqa
    from esmerald.routing.router import (
        HTTPHandler as HTTPHandler,  # noqa
        Router,
        WebSocketHandler as WebSocketHandler,  # noqa
    )
    from esmerald.websockets import WebSocket  # noqa
else:
    HTTPHandler = Any
    Application = Any
    Message = Any
    Receive = Any
    Scope = Any
    Send = Any
    BaseHTTPMiddleware = Any
    Inject = Any
    Request = Any
    WebSocket = Any
    State = Any
    Response = Any
    ResponseHeader = Any
    Cookie = Any
    Router = Any
    MiddlewareProtocol = Any
    View = Any
    Gateway = Any
    WebhookGateway = Any
    Esmerald = Any
    EsmeraldAPISettings = Any

AsyncAnyCallable = Callable[..., Awaitable[Any]]
HTTPMethod = Literal["GET", "POST", "DELETE", "PATCH", "PUT", "HEAD"]
HTTPMethods = get_args(HTTPMethod)

Middleware = DefineMiddleware

ResponseType = Type[Response]

Dependencies = Dict[str, Inject]

ExceptionType = TypeVar("ExceptionType", bound=Exception)
ExceptionHandler = Callable[[Request, ExceptionType], Response]
ExceptionHandlerMap = Mapping[Union[int, Type[Exception]], ExceptionHandler]

_ReservedKwargs = Literal[
    "request", "socket", "headers", "query", "cookies", "state", "data", "payload"
]

ReservedKwargs = get_args(_ReservedKwargs)

ResponseHeaders = Dict[str, ResponseHeader]
ResponseCookies = List[Cookie]
AsyncAnyCallable = Callable[..., Awaitable[Any]]  # type: ignore

SchedulerType = AsyncIOScheduler
DatetimeType = TypeVar("DatetimeType", bound=datetime)

ParentType = Union[View, Router, Gateway, WebSocketGateway, Esmerald, Include, Application]
APIGateHandler = Union[
    Gateway,
    WebSocketGateway,
]

RouteParent = Union["Router", "Include", ASGIApp, "Gateway", "WebSocketGateway", "WebhookGateway"]

BackgroundTaskType = Union[BackgroundTask, BackgroundTasks]
SecurityScheme = Dict[str, List[str]]

ConnectionType = Union["Request", "WebSocket"]
DictStr = Dict[str, str]
DictAny = Dict[str, Any]
SettingsType = Type["EsmeraldAPISettings"]

LifeSpanHandler = Union[Callable[[], None], Callable[[], Awaitable[None]]]
