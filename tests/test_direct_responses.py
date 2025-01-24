import json
from typing import Optional

from pydantic import BaseModel

from esmerald import Esmerald, Form, Redirect, Request, Template
from esmerald.config.template import TemplateConfig
from esmerald.responses.base import RedirectResponse
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get, route
from esmerald.testclient import EsmeraldTestClient


class Model(BaseModel):
    id: int


def test_return_response_container(template_dir):
    @get()
    async def start(request: Request) -> Template:
        return Redirect(path="/home", status_code=301)

    app = Esmerald(
        routes=[Gateway("/", handler=start)],
        template_config=TemplateConfig(
            directory=template_dir,
        ),
        middleware=[],
    )
    client = EsmeraldTestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 301


def test_return_response(template_dir):
    @get()
    async def start(request: Request) -> Template:
        return RedirectResponse(url="/home", status_code=301)

    app = Esmerald(
        routes=[Gateway("/", handler=start)],
        template_config=TemplateConfig(
            directory=template_dir,
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 301


def test_return_response_route_form(template_dir):
    @route(methods=["GET", "POST"])
    async def start(request: Request, form: Optional[Model] = Form()) -> Template:
        if request.method == "POST":
            assert form.id == 55
        return RedirectResponse(url="/home", status_code=301)

    app = Esmerald(
        routes=[Gateway("/", handler=start)],
        template_config=TemplateConfig(
            directory=template_dir,
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 301

    response = client.post("/", data={"form": json.dumps({"id": 55})}, follow_redirects=False)
    assert response.status_code == 301


def test_return_response_route_data(template_dir):
    @route(methods=["GET", "POST"])
    async def start(request: Request, data: Optional[Model] = Form()) -> Template:
        if request.method == "POST":
            assert data.id == 55
        return RedirectResponse(url="/home", status_code=301)

    app = Esmerald(
        routes=[Gateway("/", handler=start)],
        template_config=TemplateConfig(
            directory=template_dir,
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 301

    response = client.post("/", data={"id": 55}, follow_redirects=False)
    assert response.status_code == 301
