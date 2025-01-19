import pytest
from lilya.compat import reverse

from esmerald import Controller, Gateway, Include, get, post
from esmerald.testclient import create_client


@get("/hello")
async def get_hello() -> str:
    return "Hello World"


@post("/new")
async def post_new() -> str:
    return "New World"


class TestController(Controller):
    @get("/int", name="int")
    async def get_int(self, id: int) -> int:
        return id


routes = [
    Include(
        "/api",
        routes=[
            Include(
                routes=[
                    Gateway(handler=get_hello, name="hello"),
                    Gateway(handler=post_new, name="new"),
                    Gateway(handler=TestController, name="test"),
                ],
                name="v1",
            ),
        ],
        name="api",
    ),
]


@pytest.mark.filterwarnings(r"ignore" r":UserWarning")
def test_can_reverse_lookup(test_client_factory):
    with create_client(routes=routes) as client:
        app = client.app

        assert app.path_for("api:v1:hello") == "/api/hello"
        assert app.path_for("api:v1:new") == "/api/new"
        assert reverse("api:v1:hello") == "/api/hello"
        assert reverse("api:v1:new") == "/api/new"

        assert app.path_for("api:v1:int") == "/api/int"
        assert reverse("api:v1:int") == "/api/int"
