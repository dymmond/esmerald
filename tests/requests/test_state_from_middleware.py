from typing import Dict

from lilya.types import ASGIApp, Receive, Scope, Send

from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.testclient import create_client


class StateRequestMiddleWare(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp"):
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        scope["state"]["test"] = "test"
        await self.app(scope, receive, send)


def test_state_from_middleware() -> None:
    @get(path="/")
    async def get_state(request: Request) -> Dict[str, str]:
        return {"state": request.state.test}

    with create_client(
        routes=[Gateway(path="/", handler=get_state)],
        middleware=[StateRequestMiddleWare],
    ) as client:
        response = client.get("/")
        assert response.json() == {"state": "test"}
