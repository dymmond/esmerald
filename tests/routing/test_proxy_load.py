from ravyn import ChildRavyn, Gateway, Include, Response, get
from ravyn.testclient import create_client
from ravyn.utils.enums import MediaType


@get()
def home() -> str:
    return "Hello, from proxy"


@get(media_type=MediaType.JSON)
def user(user: str) -> Response:
    return Response(f"Hello, {user}")


child_esmerald = ChildRavyn(
    routes=[Gateway("/home", handler=home)],
)


def test_can_load_from_proxy(test_client_factory):
    with create_client(
        routes=[
            Gateway("/{user}", handler=user),
            Include("/child", app="tests.routing.test_proxy_load.child_esmerald"),
        ]
    ) as client:
        response = client.get("/child/home")

        assert response.status_code == 200
        assert response.text == '"Hello, from proxy"'

        response = client.get("/ravyn")

        assert response.status_code == 200
        assert response.text == "Hello, ravyn"
