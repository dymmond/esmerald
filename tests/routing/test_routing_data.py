from typing import Optional

from pydantic import BaseModel

from ravyn import Form, Ravyn, Request
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import route
from ravyn.testclient import RavynTestClient


class Model(BaseModel):
    id: str


def test_get_and_post():
    @route(methods=["GET", "POST"])
    async def start(request: Request, data: Optional[Model] = Form()) -> bytes:
        return b"hello world"

    app = Ravyn(
        debug=True,
        routes=[Gateway("/", handler=start)],
    )
    client = RavynTestClient(app)
    response = client.get("/")
    assert response.status_code == 200
