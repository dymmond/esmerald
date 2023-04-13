from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

from starlette.middleware import Middleware as StarletteMiddleware  # noqa
from starlette.responses import Response as StarletteResponse  # noqa
from starlette.types import ASGIApp  # noqa
from typing_extensions import Literal

from esmerald.backgound import BackgroundTask, BackgroundTasks
from esmerald.exceptions import HTTPException, MissingDependency, StarletteHTTPException
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.router import Include

try:
    from asyncz.schedulers import AsyncIOScheduler  # noqa
except ImportError:
    AsyncIOScheduler = Any

try:
    from esmerald.config.template import TemplateConfig as TemplateConfig  # noqa
except MissingDependency:
    TemplateConfig = Any

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.conf.global_settings import EsmeraldAPISettings  # noqa
    from esmerald.datastructures import Cookie, ResponseHeader, State  # noqa: TC004
    from esmerald.injector import Inject  # noqa
    from esmerald.protocols.middleware import MiddlewareProtocol
    from esmerald.requests import Request  # noqa
    from esmerald.responses import Response  # noqa
    from esmerald.routing.router import Gateway, HTTPHandler, Router  # noqa
    from esmerald.routing.views import APIView  # noqa
    from esmerald.websockets import WebSocket  # noqa
else:
    HTTPHandler = Any
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
    APIView = Any
    Gateway = Any
    Esmerald = Any

AsyncAnyCallable = Callable[..., Awaitable[Any]]
HTTPMethod = Literal["GET", "POST", "DELETE", "PATCH", "PUT", "HEAD"]

Middleware = Union[
    StarletteMiddleware,
    Type[MiddlewareProtocol],
    Callable[..., ASGIApp],
]

ResponseType = Type[Response]

Dependencies = Dict[str, Inject]

CoroutineHandler = Coroutine[Any, Any, Response]
ExceptionHandler = Union[
    Callable[
        [Request, Union[Exception, HTTPException, StarletteHTTPException]],
        StarletteResponse,
    ],
    Callable[[Response, Any], CoroutineHandler],
]
ExceptionHandlers = Dict[Union[int, Type[Exception]], ExceptionHandler]

ReservedKwargs = Literal[
    "request",
    "socket",
    "headers",
    "query",
    "cookies",
    "state",
    "data",
]

ResponseHeaders = Dict[str, ResponseHeader]
ResponseCookies = List[Cookie]
AsyncAnyCallable = Callable[..., Awaitable[Any]]


SchedulerType = AsyncIOScheduler
DatetimeType = TypeVar("DatetimeType", bound=datetime)

ParentType = Union[APIView, Router]
APIGateHandler = Union[
    Gateway,
    WebSocketGateway,
]

RouteParent = Union["Router", "Include", "ASGIApp", "Gateway", "WebSocketGateway"]

BackgroundTaskType = Union[BackgroundTask, BackgroundTasks]
SecurityRequirement = Dict[str, List[str]]

ConnectionType = Union["Request", "WebSocket"]
DictStr = Dict[str, str]
DictAny = Dict[str, Any]
SettingsType = Type["EsmeraldAPISettings"]

LifeSpanHandler = Union[
    Callable[[], Any],
    Callable[[State], Any],
    Callable[[], Awaitable[Any]],
    Callable[[State], Awaitable[Any]],
]
