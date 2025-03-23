import os

import pytest

from esmerald.applications import Esmerald
from esmerald.config.template import TemplateConfig
from esmerald.datastructures import Template
from esmerald.requests import Request
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.template.jinja import JinjaTemplateEngine
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


@pytest.mark.parametrize("apostrophe", ["'", '"'])
def test_templates_starlette(template_dir, test_client_factory, apostrophe):
    path = os.path.join(template_dir, "index.html")
    with open(path, "w") as file:
        file.write(
            "<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>".replace(
                "'", apostrophe
            )
        )

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
    assert response.text == "<html>Hello, <a href='http://testserver/'>world</a></html>".replace(
        "'", apostrophe
    )


def test_templates_async(template_dir, test_client_factory):
    path = os.path.join(template_dir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello {{ say_world() }}</html>")

    async def say_world():
        return "world"

    @get()
    async def homepage(request: Request) -> Template:
        return Template(name="index.html", context={"request": request, "say_world": say_world})

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=homepage)],
        template_config=TemplateConfig(
            directory=template_dir, engine=JinjaTemplateEngine, env_options={"enable_async": True}
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.text == "<html>Hello world</html>"


def test_alternative_template(template_dir, test_client_factory):
    path = os.path.join(template_dir, "index.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    @get()
    async def homepage(request: Request) -> Template:
        return Template(
            name="indx.html", context={"request": request}, alternative_template="index.html"
        )

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
