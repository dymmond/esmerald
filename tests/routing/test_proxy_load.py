from esmerald import ChildEsmerald, Gateway, Include, Response, get
from esmerald.enums import MediaType
from esmerald.testclient import create_client


@get()
def home() -> str:
    return "Hello, from proxy"


@get(media_type=MediaType.JSON)
def user(user: str) -> Response:
    return Response(f"Hello, {user}")


child_esmerald = ChildEsmerald(
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

        response = client.get("/esmerald")

        assert response.status_code == 200
        assert response.text == '"Hello, esmerald"'
