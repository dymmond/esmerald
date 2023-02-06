import os
import pathlib

import pytest

from esmerald.applications import Esmerald
from esmerald.config.template import TemplateConfig
from esmerald.datastructures import Template
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.template.jinja import JinjaTemplateEngine
from esmerald.template.mako import MakoTemplateEngine
from esmerald.testclient import EsmeraldTestClient, create_client


def test_handler_raise_for_no_template_engine_created() -> None:
    @get(path="/")
    def invalid_path() -> Template:
        return Template(name="index.html", context={"ye": "yeeee"})

    with create_client(routes=[Gateway(handler=invalid_path)]) as client:
        response = client.request("GET", "/")
        assert response.status_code == 500
        assert response.json() == {
            "detail": "Template engine is not configured",
        }
        assert response.status_code == 500


@pytest.mark.parametrize("engine", [JinjaTemplateEngine, MakoTemplateEngine])
def test_engine_jinja_and_mako(engine, template_dir: "pathlib.Path") -> None:
    app = Esmerald(
        routes=[],
        template_config=TemplateConfig(
            directory=template_dir,
            engine=engine,
        ),
    )

    assert isinstance(app.template_engine, engine)


def test_templates_starlette(template_dir, test_client_factory):
    path = os.path.join(template_dir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    @get()
    async def homepage(request: Request) -> Template:
        return Template(name="index.html", context={"request": request})

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=homepage)],
        template_config=TemplateConfig(
            directory=template_dir,
            engine=JinjaTemplateEngine,
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>"
