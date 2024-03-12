import inspect
import typing

from starlette._exception_handler import (
    ExceptionHandlers,
    StatusHandlers,
    _lookup_exception_handler,
)
from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.websockets import WebSocket


def wrap_app_handling_exceptions(app: ASGIApp, conn: typing.Union[Request, WebSocket]) -> ASGIApp:
    exception_handlers: ExceptionHandlers
    status_handlers: StatusHandlers
    try:
        exception_handlers, status_handlers = conn.scope["starlette.exception_handlers"]
    except KeyError:  # pragma: no cover
        exception_handlers, status_handlers = {}, {}

    async def wrapped_app(scope: Scope, receive: Receive, send: Send) -> None:
        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await app(scope, receive, sender)
        except Exception as exc:
            handler = None

            if isinstance(exc, HTTPException):
                handler = status_handlers.get(exc.status_code)

            if handler is None:
                handler = _lookup_exception_handler(exception_handlers, exc)

            if handler is None:
                raise exc

            if response_started:  # pragma: no cover
                msg = "Caught handled exception, but response already started."
                raise RuntimeError(msg) from exc

            if scope["type"] == "http":
                response: Response
                if is_async_callable(handler):
                    response = await handler(conn, exc)
                else:
                    response = await run_in_threadpool(
                        typing.cast("typing.Callable[..., Response]", handler), conn, exc
                    )
                await response(scope, receive, sender)
            elif scope["type"] == "websocket":
                if is_async_callable(handler):
                    if inspect.isfunction(handler):
                        await app(scope, receive, send)
                    else:
                        await handler(conn, exc)
                else:
                    await run_in_threadpool(handler, conn, exc)  # type: ignore

    return wrapped_app
