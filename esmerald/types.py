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

from esmerald.backgound import BackgroundTask, BackgroundTasks
from esmerald.exceptions import HTTPException, StarletteHTTPException
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.router import Include
from esmerald.schedulers import AsyncIOScheduler
from pydantic.typing import AnyCallable
from starlette.responses import Response as StarletteResponse
from typing_extensions import Literal

if TYPE_CHECKING:
    from esmerald.datastructures import Cookie, ResponseHeader, State  # noqa: TC004
    from esmerald.injector import Inject  # noqa
    from esmerald.protocols.middleware import MiddlewareProtocol
    from esmerald.requests import Request  # noqa
    from esmerald.responses import Response  # noqa
    from esmerald.routing.router import Gateway, HTTPHandler, Router  # noqa
    from esmerald.routing.views import APIView  # noqa
    from esmerald.websockets import WebSocket  # noqa
    from starlette.middleware import Middleware as StarletteMiddleware  # noqa: TC004
    from starlette.middleware.base import BaseHTTPMiddleware  # noqa: TC004
    from starlette.types import ASGIApp as ASGIApp  # noqa
    from starlette.types import Message as Message  # noqa
    from starlette.types import Receive as Receive  # noqa
    from starlette.types import Scope as Scope  # noqa
    from starlette.types import Send as Send  # noqa
else:
    ASGIApp = Any
    HTTPHandler = Any
    Message = Any
    Receive = Any
    Scope = Any
    Send = Any
    StarletteMiddleware = Any
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

AsyncAnyCallable = Callable[..., Awaitable[Any]]
HTTPMethod = Literal["GET", "POST", "DELETE", "PATCH", "PUT", "HEAD"]

Middleware = Union[
    StarletteMiddleware,
    Type[BaseHTTPMiddleware],
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

LifeSpanHandler = Union[
    Callable[[], Any],
    Callable[[State], Any],
    Callable[[], Awaitable[Any]],
    Callable[[State], Awaitable[Any]],
]

SchedulerType = AsyncIOScheduler
DatetimeType = TypeVar("DatetimeType", bound=datetime)

ParentType = Union[APIView, Router]
APIGateHandler = Union[
    Type[APIView],
    HTTPHandler,
    Router,
    AnyCallable,
    Gateway,
    WebSocketGateway,
]

RouteParent = Union["Router", "Include", "ASGIApp", "Gateway", "WebSocketGateway"]

BackgroundTaskType = Union[BackgroundTask, BackgroundTasks]
SecurityRequirement = Dict[str, List[str]]

ConnectionType = Union["Request", "WebSocket"]
DictStr = Dict[str, str]
