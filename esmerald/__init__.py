__version__ = "3.7.3"

from typing import TYPE_CHECKING

from monkay import Monkay

if TYPE_CHECKING:
    from lilya import status

    from esmerald.conf import settings
    from esmerald.conf.global_settings import EsmeraldAPISettings
    from esmerald.context import Context
    from esmerald.core.datastructures import JSON, Redirect, Stream, Template, UploadFile
    from esmerald.injector import Factory, Inject

    from .applications import ChildEsmerald, Esmerald
    from .background import BackgroundTask, BackgroundTasks
    from .core.config import (
        CORSConfig,
        CSRFConfig,
        OpenAPIConfig,
        SessionConfig,
        StaticFilesConfig,
    )
    from .core.interceptors.interceptor import EsmeraldInterceptor
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
    from .param_functions import Requires, Security
    from .params import Body, Cookie, File, Form, Header, Injects, Param, Path, Query
    from .permissions import AllowAny, BasePermission, DenyAll
    from .pluggables import Extension, Pluggable
    from .protocols import AsyncDAOProtocol, DaoProtocol, MiddlewareProtocol
    from .requests import Request
    from .responses import JSONResponse, Response, TemplateResponse
    from .routing.apis import APIView, Controller, SimpleAPIView, View
    from .routing.gateways import Gateway, WebhookGateway, WebSocketGateway
    from .routing.handlers import (
        delete,
        get,
        head,
        options,
        patch,
        post,
        put,
        route,
        trace,
        websocket,
    )
    from .routing.router import Host, Include, Router
    from .routing.webhooks import (
        whdelete,
        whget,
        whhead,
        whoptions,
        whpatch,
        whpost,
        whput,
        whroute,
        whtrace,
    )
    from .utils.decorators import observable
    from .websockets import WebSocket, WebSocketDisconnect, WebSocketState

__all__ = [
    "AllowAny",
    "APIView",
    "AsyncDAOProtocol",
    "BackgroundTask",
    "BackgroundTasks",
    "Body",
    "BasePermission",
    "ChildEsmerald",
    "Context",
    "Controller",
    "CORSConfig",
    "CSRFConfig",
    "Cookie",
    "DaoProtocol",
    "DenyAll",
    "Esmerald",
    "EsmeraldAPISettings",
    "EsmeraldInterceptor",
    "Extension",
    "File",
    "Form",
    "Gateway",
    "Header",
    "HTTPException",
    "Include",
    "Inject",
    "Factory",
    "Host",
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
    "Pluggable",
    "Query",
    "Redirect",
    "Request",
    "Requires",
    "Response",
    "Router",
    "Security",
    "ServiceUnavailable",
    "SessionConfig",
    "SimpleAPIView",
    "StaticFilesConfig",
    "Stream",
    "Template",
    "TemplateResponse",
    "UploadFile",
    "ValidationErrorException",
    "View",
    "WebhookGateway",
    "WebSocket",
    "WebSocketDisconnect",
    "WebSocketGateway",
    "WebSocketState",
    "delete",
    "get",
    "head",
    "observable",
    "options",
    "patch",
    "post",
    "put",
    "route",
    "settings",
    "status",
    "trace",
    "websocket",
    "whdelete",
    "whhead",
    "whget",
    "whoptions",
    "whpatch",
    "whpost",
    "whput",
    "whroute",
    "whtrace",
]

_monkay: Monkay = Monkay(
    globals(),
    lazy_imports={
        "status": "lilya.status",
        "settings": ".conf.settings",
        "EsmeraldAPISettings": ".conf.global_settings.EsmeraldAPISettings",
        "Context": "esmerald.context.Context",
        "JSON": ".core.datastructures.JSON",
        "Redirect": ".core.datastructures.Redirect",
        "Stream": ".core.datastructures.Stream",
        "Template": ".core.datastructures.Template",
        "UploadFile": ".core.datastructures.UploadFile",
        "Factory": "esmerald.injector.Factory",
        "Inject": "esmerald.injector.Inject",
        "ChildEsmerald": ".applications.ChildEsmerald",
        "Esmerald": ".applications.Esmerald",
        "BackgroundTask": ".background.BackgroundTask",
        "BackgroundTasks": ".background.BackgroundTasks",
        "CORSConfig": ".core.config.CORSConfig",
        "CSRFConfig": ".core.config.CSRFConfig",
        "OpenAPIConfig": ".core.config.OpenAPIConfig",
        "SessionConfig": ".core.config.SessionConfig",
        "StaticFilesConfig": ".core.config.StaticFilesConfig",
        "EsmeraldInterceptor": ".core.interceptors.interceptor.EsmeraldInterceptor",
        "HTTPException": ".exceptions.HTTPException",
        "ImproperlyConfigured": ".exceptions.ImproperlyConfigured",
        "MethodNotAllowed": ".exceptions.MethodNotAllowed",
        "NotAuthenticated": ".exceptions.NotAuthenticated",
        "NotFound": ".exceptions.NotFound",
        "PermissionDenied": ".exceptions.PermissionDenied",
        "ServiceUnavailable": ".exceptions.ServiceUnavailable",
        "ValidationErrorException": ".exceptions.ValidationErrorException",
        "Requires": ".param_functions.Requires",
        "Security": ".param_functions.Security",
        "Body": ".params.Body",
        "Cookie": ".params.Cookie",
        "File": ".params.File",
        "Form": ".params.Form",
        "Header": ".params.Header",
        "Injects": ".params.Injects",
        "Param": ".params.Param",
        "Path": ".params.Path",
        "Query": ".params.Query",
        "AllowAny": ".permissions.AllowAny",
        "BasePermission": ".permissions.BasePermission",
        "DenyAll": ".permissions.DenyAll",
        "Extension": ".pluggables.Extension",
        "Pluggable": ".pluggables.Pluggable",
        "AsyncDAOProtocol": ".protocols.AsyncDAOProtocol",
        "DaoProtocol": ".protocols.DaoProtocol",
        "MiddlewareProtocol": ".protocols.MiddlewareProtocol",
        "Request": ".requests.Request",
        "JSONResponse": ".responses.JSONResponse",
        "Response": ".responses.Response",
        "TemplateResponse": ".responses.TemplateResponse",
        "APIView": ".routing.apis.APIView",
        "Controller": ".routing.apis.Controller",
        "SimpleAPIView": ".routing.apis.SimpleAPIView",
        "View": ".routing.apis.View",
        "Gateway": ".routing.gateways.Gateway",
        "WebhookGateway": ".routing.gateways.WebhookGateway",
        "WebSocketGateway": ".routing.gateways.WebSocketGateway",
        "websocket": ".routing.handlers.websocket",  # rest is autogenerated
        "Host": ".routing.router.Host",
        "Include": ".routing.router.Include",
        "Router": ".routing.router.Router",
        "observable": ".utils.decorators.observable",
        "WebSocket": ".websockets.WebSocket",
        "WebSocketDisconnect": ".websockets.WebSocketDisconnect",
        "WebSocketState": ".websockets.WebSocketState",
    },
    skip_all_update=True,
    package="esmerald",
)
for name in ["delete", "get", "head", "options", "patch", "post", "put", "route", "trace"]:
    _monkay.add_lazy_import(name, f".routing.handlers.{name}")
    _monkay.add_lazy_import(f"wh{name}", f".routing.webhooks.wh{name}")
del name
