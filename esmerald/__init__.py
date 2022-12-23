"""
Esmerald: Highly scalable, performant, easy to learn and for every application.
"""
__version__ = "0.5.1"

from starlette import status

from esmerald.conf import settings
from esmerald.conf.global_settings import EsmeraldAPISettings
from esmerald.injector import Inject

from .applications import ChildEsmerald, Esmerald
from .backgound import BackgroundTask, BackgroundTasks
from .config import (
    CORSConfig,
    CSRFConfig,
    JWTConfig,
    OpenAPIConfig,
    SessionConfig,
    StaticFilesConfig,
    TemplateConfig,
)
from .datastructures import UploadFile
from .exceptions import (
    HTTPException,
    ImproperlyConfigured,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ServiceUnavailable,
    ValidationErrorException,
)
from .params import Body, Cookie, Header, Injects, Param, Path, Query
from .permissions import AllowAny, BasePermission, DenyAll
from .protocols import AsyncDAOProtocol, DaoProtocol, MiddlewareProtocol
from .requests import Request
from .responses import JSONResponse, ORJSONResponse, Response, TemplateResponse, UJSONResponse
from .routing.gateways import Gateway, WebSocketGateway
from .routing.handlers import delete, get, patch, post, put, route, websocket
from .routing.router import Include, Router
from .routing.views import APIView
from .schedulers.asyncz.handler import scheduler
from .template import JinjaTemplateEngine, MakoTemplateEngine
from .websockets import WebSocket, WebSocketDisconnect

__all__ = [
    "AllowAny",
    "APIView",
    "AsyncDAOProtocol",
    "BackgroundTask",
    "BackgroundTasks",
    "Body",
    "BasePermission",
    "ChildEsmerald",
    "CORSConfig",
    "CSRFConfig",
    "Cookie",
    "DaoProtocol",
    "DenyAll",
    "Esmerald",
    "EsmeraldAPISettings",
    "Gateway",
    "Header",
    "HTTPException",
    "Include",
    "Inject",
    "Injects",
    "ImproperlyConfigured",
    "JSONResponse",
    "JinjaTemplateEngine",
    "JWTConfig",
    "MakoTemplateEngine",
    "MethodNotAllowed",
    "MiddlewareProtocol",
    "NotAuthenticated",
    "NotFound",
    "ORJSONResponse",
    "OpenAPIConfig",
    "Param",
    "Path",
    "PermissionDenied",
    "Query",
    "Request",
    "Response",
    "Router",
    "ServiceUnavailable",
    "SessionConfig",
    "StaticFilesConfig",
    "TemplateConfig",
    "TemplateResponse",
    "UJSONResponse",
    "UploadFile",
    "ValidationErrorException",
    "WebSocket",
    "WebSocketDisconnect",
    "WebSocketGateway",
    "delete",
    "get",
    "patch",
    "post",
    "put",
    "route",
    "scheduler",
    "settings",
    "status",
    "websocket",
]
