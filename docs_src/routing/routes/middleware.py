from esmerald import Esmerald, Gateway, MiddlewareProtocol, get
from esmerald.types import ASGIApp


class RequestLoggingMiddlewareProtocol(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", kwargs: str = "") -> None:
        self.app = app
        self.kwargs = kwargs


class ExampleMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp") -> None:
        self.app = app


@get(path="/home", middleware=[RequestLoggingMiddlewareProtocol])
async def homepage() -> dict:
    return {"page": "ok"}


app = Esmerald(routes=[Gateway(handler=homepage, middleware=[ExampleMiddleware])])
