import logging
from typing import Any, Awaitable, Callable, List, Type, cast

from _pytest.logging import LogCaptureFixture
from lilya.middleware.cors import CORSMiddleware
from lilya.middleware.trustedhost import TrustedHostMiddleware
from lilya.types import ASGIApp, Receive, Scope, Send
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from esmerald.applications import ChildEsmerald
from esmerald.config import CORSConfig
from esmerald.enums import ScopeType
from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get, post
from esmerald.routing.router import Include
from esmerald.testclient import create_client

logger = logging.getLogger(__name__)


class MiddlewareProtocolRequestLoggingMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp", kwarg: str = "") -> None:
        self.app = app
        self.kwarg = kwarg

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope["type"] == ScopeType.HTTP:
            request = Request(scope=scope, receive=receive)
            body = await request.json()
            logger.info(f"test logging: {request.method}, {request.url}, {body}")
        await self.app(scope, receive, send)


class BaseMiddlewareRequestLoggingMiddleware(BaseHTTPMiddleware):  # pragma: no cover
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore
        logging.getLogger(__name__).info("%s - %s", request.method, request.url)
        return await call_next(request)  # type: ignore


class MiddlewareWithArgsAndKwargs(BaseHTTPMiddleware):  # pragma: no cover
    def __init__(self, arg: int = 0, *, app: Any, kwarg: str) -> None:
        super().__init__(app)
        self.arg = arg
        self.kwarg = kwarg

    async def dispatch(  # type: ignore
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response: ...


@get(path="/")
def handler() -> None:
    """ """


class JSONRequest(BaseModel):
    name: str
    age: int
    programmer: bool


@post(path="/")
def post_handler(data: JSONRequest) -> JSONRequest:
    return data


def test_setting_cors_middleware() -> None:
    cors_config = CORSConfig()
    assert cors_config.allow_credentials is False
    assert cors_config.allow_headers == ["*"]
    assert cors_config.allow_methods == ["*"]
    assert cors_config.allow_origins == ["*"]
    assert cors_config.allow_origin_regex is None
    assert cors_config.max_age == 600
    assert cors_config.expose_headers == []

    with create_client(
        routes=[Gateway(path="/", handler=handler)], cors_config=cors_config
    ) as client:
        unpacked_middleware = []
        _ids = []
        cur = client.app.router

        while hasattr(cur, "app"):
            unpacked_middleware.extend(cur._app.user_middleware)
            _ids.append(id(cur._app.user_middleware))
            cur = cast("Any", cur._app)  # type: ignore

        assert len(unpacked_middleware) == 2
        cors_middleware = cast("Any", unpacked_middleware[1])

        assert isinstance(cors_middleware.middleware, type(CORSMiddleware))
        assert cors_middleware.kwargs["allow_headers"] == ["*"]
        assert cors_middleware.kwargs["allow_methods"] == ["*"]
        assert cors_middleware.kwargs["allow_origins"] == cors_config.allow_origins
        assert cors_middleware.kwargs["allow_origins"] == cors_config.allow_origins


def test_trusted_hosts_middleware() -> None:
    client = create_client(routes=[Gateway(path="/", handler=handler)], allowed_hosts=["*"])
    unpacked_middleware = []
    _ids = []

    cur = client.app.router

    while hasattr(cur, "app"):
        unpacked_middleware.extend(cur._app.user_middleware)
        _ids.append(id(cur._app.user_middleware))
        cur = cast("Any", cur._app)  # type: ignore

    assert len(unpacked_middleware) == 1
    trusted_hosts_middleware = cast("Any", unpacked_middleware[0])
    assert isinstance(trusted_hosts_middleware.middleware, type(TrustedHostMiddleware))
    assert trusted_hosts_middleware.kwargs["allowed_hosts"] == ["*"]


def test_request_body_logging_middleware(caplog: "LogCaptureFixture") -> None:
    with caplog.at_level(logging.INFO):
        client = create_client(
            routes=[Gateway(path="/", handler=post_handler)],
            middleware=[MiddlewareProtocolRequestLoggingMiddleware],
        )
        response = client.post("/", json={"name": "moishe zuchmir", "age": 40, "programmer": True})
        assert response.status_code == 201
        assert "test logging" in caplog.text


def test_middleware_call_order() -> None:
    """Test that middlewares are called in the order they have been passed."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    with create_client(
        routes=[
            Gateway(
                path="/router",
                handler=MyController,
                middleware=[create_test_middleware(2), create_test_middleware(3)],
            )
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/router/controller/handler")

        assert results == [0, 1, 2, 3, 4, 5, 6, 7]


def test_middleware_call_order_with_include() -> None:
    """Test that middlewares are called in the order they have been passed with include."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    with create_client(
        routes=[
            Include(
                routes=[Gateway(path="/", handler=MyController)],
                middleware=[create_test_middleware(2), create_test_middleware(3)],
            ),
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/controller/handler")
        assert results == [0, 1, 2, 3, 4, 5, 6, 7]


def test_middleware_call_order_with_nested_include() -> None:
    """Test that middlewares are called in the order they have been passed with nested include."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    with create_client(
        routes=[
            Include(
                path="/",
                routes=[
                    Include(
                        path="/",
                        routes=[Gateway(path="/", handler=MyController)],
                        middleware=[
                            create_test_middleware(2),
                            create_test_middleware(3),
                        ],
                    ),
                ],
            ),
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/controller/handler")

        assert results == [0, 1, 2, 3, 4, 5, 6, 7]


def test_middleware_call_order_with_heavy_nested_include() -> None:
    """Test that middlewares are called in the order they have been passed with heavy nested includes."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    with create_client(
        routes=[
            Include(
                path="/",
                routes=[
                    Include(
                        path="/",
                        routes=[
                            Include(
                                path="/",
                                routes=[
                                    Include(
                                        path="/",
                                        routes=[
                                            Include(
                                                path="/",
                                                routes=[
                                                    Include(
                                                        path="/",
                                                        routes=[
                                                            Include(
                                                                path="/",
                                                                routes=[
                                                                    Include(
                                                                        path="/",
                                                                        routes=[
                                                                            Include(
                                                                                path="/",
                                                                                routes=[
                                                                                    Include(
                                                                                        path="/",
                                                                                        routes=[
                                                                                            Gateway(
                                                                                                path="/",
                                                                                                handler=MyController,
                                                                                            )
                                                                                        ],
                                                                                        middleware=[
                                                                                            create_test_middleware(
                                                                                                2
                                                                                            ),
                                                                                            create_test_middleware(
                                                                                                3
                                                                                            ),
                                                                                        ],
                                                                                    ),
                                                                                ],
                                                                            )
                                                                        ],
                                                                    )
                                                                ],
                                                            )
                                                        ],
                                                    )
                                                ],
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/controller/handler")

        assert results == [0, 1, 2, 3, 4, 5, 6, 7]


def test_middleware_call_order_with_child_esmerald() -> None:
    """Test that middlewares are called in the order they have been passed with include."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    child_esmerald = ChildEsmerald(routes=[Gateway(path="/", handler=MyController)])

    with create_client(
        routes=[
            Include(
                path="/child",
                routes=[
                    Include(
                        path="/esmerald",
                        routes=[Include(routes=[Include(app=child_esmerald)])],
                    )
                ],
                middleware=[create_test_middleware(2), create_test_middleware(3)],
            ),
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/child/esmerald/controller/handler")

        assert results == [0, 1, 2, 3, 4, 5, 6, 7]


def test_middleware_call_order_with_child_esmerald_as_parent() -> None:
    """Test that middlewares are called in the order they have been passed with include."""

    results: List[int] = []

    def create_test_middleware(middleware_id: int) -> "Type[MiddlewareProtocol]":
        class TestMiddleware(MiddlewareProtocol):
            def __init__(self, app: "ASGIApp") -> None:
                self.app = app

            async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                results.append(middleware_id)
                await self.app(scope, receive, send)

        return TestMiddleware

    class MyController(APIView):
        path = "/controller"
        middleware = [create_test_middleware(4), create_test_middleware(5)]

        @get(
            "/handler",
            middleware=[create_test_middleware(6), create_test_middleware(7)],
        )
        def my_handler(self) -> None:
            """ """

    child_esmerald = ChildEsmerald(routes=[Gateway(path="/", handler=MyController)])

    with create_client(
        routes=[
            Include(
                path="/child",
                routes=[
                    Include(
                        path="/esmerald",
                        routes=[
                            Include(
                                routes=[Include(app=child_esmerald)],
                                middleware=[
                                    create_test_middleware(2),
                                    create_test_middleware(3),
                                ],
                            )
                        ],
                    )
                ],
            ),
        ],
        middleware=[
            create_test_middleware(0),
            create_test_middleware(1),
        ],
    ) as client:
        client.get("/child/esmerald/controller/handler")

        assert results == [0, 1, 2, 3, 4, 5, 6, 7]
