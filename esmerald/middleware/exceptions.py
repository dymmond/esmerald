import inspect
from inspect import getmro
from typing import Any, Callable, Dict, List, Mapping, Optional, Type, Union, cast

from pydantic import BaseModel
from starlette import status
from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware as StarletteExceptionMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from esmerald.enums import MediaType, ScopeType
from esmerald.exception_handlers import http_exception_handler
from esmerald.exceptions import HTTPException, WebSocketException
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.types import ExceptionHandler, ExceptionHandlers
from esmerald.websockets import WebSocket


class ExceptionMiddleware(StarletteExceptionMiddleware):
    """
    Reimplementation of the Exception Middleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        handlers: Optional[Mapping[Any, Callable[[Request, Exception], Response]]] = None,
        debug: bool = False,
    ) -> None:
        self.app = app
        self.debug = debug
        self._status_handlers: Dict[int, Callable] = {}
        self._exception_handlers: Dict[Type[Exception], Callable] = {
            HTTPException: http_exception_handler,
            StarletteHTTPException: http_exception_handler,
            WebSocketException: self.websocket_exception,
        }
        if handlers is not None:
            for key, value in handlers.items():
                self.add_exception_handler(key, value)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope=scope, receive=receive, send=send)
        except Exception as exc:
            handler = None

            if isinstance(exc, StarletteHTTPException):
                handler = self._status_handlers.get(exc.status_code)

            if handler is None:
                handler = self._lookup_exception_handler(exc)

            if handler is None:
                raise exc

            if response_started:
                msg = "Caught handled exception, but response already started."
                raise RuntimeError(msg) from exc

            if scope["type"] == "http":
                request = Request(scope, receive=receive)
                if is_async_callable(handler):
                    response = await handler(request, exc)
                else:
                    response = await run_in_threadpool(handler, request, exc)
                await response(scope, receive, sender)
            elif scope["type"] == "websocket":
                websocket = WebSocket(scope, receive=receive, send=send)
                if is_async_callable(handler):
                    if inspect.isfunction(handler):
                        await self.app(scope, receive, send)
                    else:
                        await handler(websocket, exc)
                else:
                    await run_in_threadpool(handler, websocket, exc)


class ResponseContent(BaseModel):
    detail: Optional[str]
    extra: Optional[Union[Dict[str, Any], List[Any]]] = None
    headers: Optional[Dict[str, str]] = None
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR


class EsmeraldAPIExceptionMiddleware:
    def __init__(
        self,
        app: "ASGIApp",
        debug: bool,
        exception_handlers: "ExceptionHandlers",
        error_handler: Optional[Callable] = None,
    ) -> None:
        self.app = app
        self.exception_handlers = exception_handlers
        self.debug = debug
        self.error_handler = error_handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as ex:
            if scope["type"] == ScopeType.HTTP:
                exception_handler = (
                    self.get_exception_handler(self.exception_handlers, ex)
                    or self.default_http_exception_handler
                )
                response = exception_handler(Request(scope, receive, send), ex)
                await response(scope, receive, send)
                return

            if isinstance(ex, WebSocketException):
                code = ex.code
                reason = ex.detail
            elif isinstance(ex, StarletteHTTPException):
                code = ex.status_code + 4000
                reason = ex.detail
            else:
                code = status.HTTP_500_INTERNAL_SERVER_ERROR + 4000
                reason = repr(ex)

            event = {"type": "websocket.close", "code": code, "reason": reason}
            await send(event)

    def default_http_exception_handler(
        self, request: Request, exc: Exception
    ) -> "StarletteResponse":
        """Default handler for exceptions subclassed from HTTPException."""
        status_code = (
            exc.status_code
            if isinstance(exc, StarletteHTTPException)
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR and self.debug:
            server_error = ServerErrorMiddleware(app=self.app, handler=self.error_handler)  # type: ignore[arg-type]
            return server_error.debug_response(request=request, exc=exc)  # type: ignore[arg-type]
        return self.create_exception_response(exc)

    def create_exception_response(self, exc: Exception) -> Response:
        if isinstance(exc, (HTTPException, StarletteHTTPException)):
            content = ResponseContent(detail=exc.detail, status_code=exc.status_code)
            if isinstance(exc, HTTPException):
                extra = exc.extra.get("extra", {})
                if extra:
                    content.extra = extra
        else:
            content = ResponseContent(detail=repr(exc))
        return Response(
            media_type=MediaType.JSON,
            content=content.dict(exclude_none=True),
            status_code=content.status_code,
            headers=exc.headers
            if isinstance(exc, (HTTPException, StarletteHTTPException))
            else None,
        )

    def get_exception_handler(
        self,
        exception_handlers: Dict[Union[int, Type[Exception]], "ExceptionHandlers"],
        exc: Exception,
    ) -> Optional[ExceptionHandler]:
        if not exception_handlers:
            return None

        if not isinstance(exc, HTTPException) and exc.__class__ in exception_handlers:
            return exception_handlers[exc.__class__]

        if isinstance(exc, HTTPException) and exc.__class__ in exception_handlers:
            return exception_handlers[exc.__class__]

        for klass in getmro(type(exc)):
            if klass in exception_handlers:
                return exception_handlers[cast("Type[Exception]", exc)]
        return None
