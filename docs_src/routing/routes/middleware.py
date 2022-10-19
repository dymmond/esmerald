from starlette.middleware.base import BaseHTTPMiddleware

from esmerald import Esmerald, Gateway, MiddlewareProtocol, get
from esmerald.types import ASGIApp


class RequestLoggingMiddlewareProtocol(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", kwargs: str = "") -> None:
        self.app = app
        self.kwargs = kwargs


class ExampleMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp") -> None:
        self.app = app


class BaseRequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore
        return await call_next(request)


@get(path="/home", middleware=[RequestLoggingMiddlewareProtocol])
async def homepage() -> dict:
    return {"page": "ok"}


app = Esmerald(
    routes=[Gateway(handler=homepage, middleware=[ExampleMiddleware])],
    middleware=[BaseRequestLoggingMiddleware],
)
