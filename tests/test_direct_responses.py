import os

from esmerald import Esmerald, Redirect, Request, Template
from esmerald.config.template import TemplateConfig
from esmerald.responses.base import RedirectResponse
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.testclient import EsmeraldTestClient


def test_return_response_container(template_dir):
    path = os.path.join(template_dir, "start.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    @get()
    async def start(request: Request) -> Template:
        return Redirect(path="/home", status_code=301)

    app = Esmerald(
        debug=True,
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
    path = os.path.join(template_dir, "start.html")
    with open(path, "w") as file:
        file.write("<html>Hello, <a href='{{ url_for('homepage') }}'>world</a></html>")

    @get()
    async def start(request: Request) -> Template:
        return RedirectResponse(url="/home", status_code=301)

    app = Esmerald(
        debug=True,
        routes=[Gateway("/", handler=start)],
        template_config=TemplateConfig(
            directory=template_dir,
        ),
    )
    client = EsmeraldTestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 301
