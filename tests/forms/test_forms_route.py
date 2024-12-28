from pydantic import BaseModel

from esmerald import Esmerald, Form, Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import route
from esmerald.testclient import EsmeraldTestClient


class Model(BaseModel):
    id: str


def test_get_and_post():
    @route(methods=["GET", "POST"])
    async def start(request: Request, form: Model | None = Form()) -> bytes:
        return b"hello world"

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=start)],
    )
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.status_code == 200
