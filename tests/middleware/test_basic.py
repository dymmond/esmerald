from esmerald import Gateway, get
from esmerald.middleware.basic import BasicHTTPMiddleware
from esmerald.testclient import create_client


@get("/home")
async def home() -> str:
    return "home"


def test_basic_middleware(test_client_factory):
    with create_client(routes=[Gateway(handler=home)], middleware=[BasicHTTPMiddleware]) as client:
        response = client.get("/home")

        assert response.status_code == 200
