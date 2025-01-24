import json
from typing import Optional, Union

import pytest
from pydantic import BaseModel

from esmerald import Esmerald, Form, Request
from esmerald.exceptions import ImproperlyConfigured
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import route
from esmerald.testclient import EsmeraldTestClient


class Model(BaseModel):
    id: str


def test_get_and_post():
    @route(methods=["GET", "POST"])
    async def start(request: Request, form: Union[Model, None] = Form()) -> bytes:
        if request.method == "POST":
            assert form.id == "733"
        return b"hello world"

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=start)],
    )
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.status_code == 200

    response = client.post("/", data={"form": json.dumps({"id": "733"})})
    assert response.status_code == 200


def test_get_and_post_optional():
    @route(methods=["GET", "POST"])
    async def start(request: Request, form: Optional[Model] = Form()) -> bytes:
        return b"hello world"

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=start)],
    )
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_get_and_head_form():
    with pytest.raises(ImproperlyConfigured):

        @route(methods=["GET", "HEAD"])
        async def start(form: Optional[Model] = Form()) -> bytes:
            return b"hello world"
