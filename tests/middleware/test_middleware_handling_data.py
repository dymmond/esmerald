import logging

from _pytest.logging import LogCaptureFixture
from lilya.types import ASGIApp, Receive, Scope, Send
from pydantic import BaseModel

from esmerald.enums import ScopeType
from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get, post
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


def test_request_body_logging_middleware(caplog: "LogCaptureFixture") -> None:
    with caplog.at_level(logging.INFO):
        client = create_client(
            routes=[Gateway(path="/", handler=post_handler)],
            middleware=[MiddlewareProtocolRequestLoggingMiddleware],
        )
        response = client.post("/", json={"name": "moishe zuchmir", "age": 40, "programmer": True})
        assert response.status_code == 201
        assert "test logging" in caplog.text
