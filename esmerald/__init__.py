"""
Esmerald: Highly scalable, performant, easy to learn and for every application.
"""
__version__ = "0.13.0"

from starlette import status

from esmerald.conf import settings
from esmerald.conf.global_settings import EsmeraldAPISettings
from esmerald.injector import Inject

from .applications import ChildEsmerald, Esmerald
from .backgound import BackgroundTask, BackgroundTasks
from .config import CORSConfig, CSRFConfig, OpenAPIConfig, SessionConfig, StaticFilesConfig
from .datastructures import JSON, Redirect, Stream, Template, UploadFile
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
from .interceptors.interceptor import EsmeraldInterceptor
from .param_functions import DirectInjects
from .params import Body, Cookie, File, Form, Header, Injects, Param, Path, Query
from .permissions import AllowAny, BasePermission, DenyAll
from .protocols import AsyncDAOProtocol, DaoProtocol, MiddlewareProtocol
from .requests import Request
from .responses import JSONResponse, Response, TemplateResponse
from .routing.gateways import Gateway, WebSocketGateway
from .routing.handlers import delete, get, patch, post, put, route, websocket
from .routing.router import Include, Router
from .routing.views import APIView
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
    "DirectInjects",
    "Esmerald",
    "EsmeraldAPISettings",
    "EsmeraldInterceptor",
    "File",
    "Form",
    "Gateway",
    "Header",
    "HTTPException",
    "Include",
    "Inject",
    "Injects",
    "ImproperlyConfigured",
    "JSON",
    "JSONResponse",
    "MethodNotAllowed",
    "MiddlewareProtocol",
    "NotAuthenticated",
    "NotFound",
    "OpenAPIConfig",
    "Param",
    "Path",
    "PermissionDenied",
    "Query",
    "Redirect",
    "Request",
    "Response",
    "Router",
    "ServiceUnavailable",
    "SessionConfig",
    "StaticFilesConfig",
    "Stream",
    "Template",
    "TemplateResponse",
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
    "settings",
    "status",
    "websocket",
]
